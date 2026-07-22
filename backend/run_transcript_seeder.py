"""
PinPulse Mock Database Seeder  (HACKATHON — Local JSON Cache)
=============================================================
Triggered when a team member uploads pinpulse_youtube_seed.xlsx.

Architecture per Excel row:
  1. YouTubeTranscriptApi  →  full transcript text
  2a. (transcript present)
      Gemini LLM → extract 2-3 garments with FULL product schema:
        item, description, tags, aesthetic, material, fabric,
        color, age_group, estimated_price_inr, occasion
  2b. (no transcript — Shorts/music-only)
      CLIP zero-shot → classify YouTube thumbnail image against
        garment-vocab to derive tags (NEW — before Gemini fallback)
      Gemini regional-context generator (fallback only if CLIP also fails)
  3. embed_dress()  →  512-dim vibe vector from TEXT fields only
  4. find_best_match_multi_query()  →  Multi-Query RRF (NEW):
       Path 1 — transcript/Gemini dress vector (top-20 candidates)
       Path 2 — CLIP thumbnail dress vector    (top-20 candidates)
       Path 3 — Regional prior vibe vector     (top-20 candidates)
       Reciprocal Rank Fusion: score = Σ 1/(60 + rank)
  5. JSON export → pinpulse_mock_db.json
       New fields per record: rrf_score, query_sources

Expected Excel columns:
  video_id   — 11-character YouTube video ID
  pincode    — ZIP code (800008 / 682001 / 752001)
  type       — 'creator' or 'boutique'
  store_name — (optional) store name for boutique entries
"""

import os
import sys
import json
import math
import re
import logging
import numpy as np
import pandas as pd
from dotenv import load_dotenv

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector
from multi_query_retrieval import (
    find_best_match_multi_query,
    classify_thumbnail_with_clip,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_transcript_seeder")

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found — LLM calls will be skipped.")

LOCAL_CATALOG_FILE = os.path.join(os.path.dirname(__file__), "local_catalog.json")
OUTPUT_FILE        = os.path.join(os.path.dirname(__file__), "pinpulse_mock_db.json")
MAX_DRESSES        = 3


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              HYBRID SCORING — three independent signals                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

AGE_RANGES = {
    "teen": (13, 19), "teens": (13, 19),
    "college": (18, 24), "18-24": (18, 24), "18-25": (18, 25),
    "young adult": (20, 28), "20-30": (20, 30),
    "25-35": (25, 35), "25-40": (25, 40),
    "30-40": (30, 40), "30-45": (30, 45),
    "35+": (35, 65), "35-50": (35, 50),
    "40+": (40, 65),
    "all ages": (13, 65), "women": (18, 55), "men": (18, 55),
}

def parse_age_range(age_str):
    if not age_str:
        return None
    s = age_str.lower().strip()
    for key, rng in AGE_RANGES.items():
        if key in s:
            return rng
    m = re.match(r"(\d+)\s*[-–]\s*(\d+)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.match(r"(\d+)\+", s)
    if m:
        return (int(m.group(1)), 65)
    return None

def age_overlap_score(dress_age_str, product_age_str):
    """
    Range overlap: 1.0 = full overlap, decays to 0.0 as gap grows.
    Returns 0.5 (neutral) when either side has no age info.
    """
    d = parse_age_range(dress_age_str)
    p = parse_age_range(product_age_str)
    if not d or not p:
        return 0.5
    overlap_lo = max(d[0], p[0])
    overlap_hi = min(d[1], p[1])
    if overlap_hi >= overlap_lo:
        return 1.0
    gap = overlap_lo - overlap_hi
    return max(0.0, 1.0 - gap / 15.0)

def price_proximity_score(dress_price, product_price):
    """
    Ratio-based proximity: 1.0 when prices equal, Gaussian decay with distance.
    Returns 0.5 (neutral) when either side has no price info.
    """
    if not dress_price or not product_price or product_price == 0:
        return 0.5
    ratio = float(dress_price) / float(product_price)
    if ratio <= 0:
        return 0.0
    return float(math.exp(-0.5 * (math.log(ratio) / 0.7) ** 2))

def cosine_similarity(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              EMBEDDING — text fields only, NOT price/age                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def embed_dress(dress_meta):
    """
    512-dim vector from TEXT fields only:
      item, description, tags, aesthetic, material, fabric, color, occasion/inventory_status.
    age_group and estimated_price_inr are excluded — handled separately via range/ratio matching.
    """
    base_tags = [
        dress_meta.get("item", ""),
        dress_meta.get("aesthetic", ""),
        dress_meta.get("material", ""),
        dress_meta.get("fabric", ""),
        dress_meta.get("color", ""),
        dress_meta.get("occasion", dress_meta.get("inventory_status", "")),
    ]
    extra_tags = dress_meta.get("tags", [])
    all_tags   = [t.lower().strip() for t in base_tags + extra_tags if t]

    festive_signals = {"festive", "wedding", "ceremonial", "bridal", "traditional", "ethnic"}
    category  = "festive" if any(t in festive_signals for t in all_tags) else "casual"
    aesthetic = dress_meta.get("aesthetic", dress_meta.get("vibe", "casual"))
    return get_vibe_vector(all_tags, category_str=category, aesthetic_str=aesthetic)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              CATALOG MATCHING — hybrid cosine + age + price                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def load_catalog():
    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def find_best_catalog_match(dress_vector, dress_meta, catalog, zip_code):
    """
    Hybrid match scoring:
      70% — cosine similarity on 512-dim text embedding
      20% — age_group range overlap     (simple range comparison)
      10% — estimated_price_inr proximity (ratio-based decay)
    """
    dress_age   = dress_meta.get("age_group", "")
    dress_price = dress_meta.get("estimated_price_inr")

    best_product, best_score = None, -1.0
    for p in catalog:
        p_zips = p.get("zip_codes", [])
        if p_zips and zip_code not in p_zips:
            continue
        p_emb = p.get("embedding", [])
        if not p_emb or len(p_emb) != len(dress_vector):
            continue
        cos_score   = cosine_similarity(dress_vector, p_emb)
        age_score   = age_overlap_score(dress_age, p.get("age_group", ""))
        price_score = price_proximity_score(dress_price, p.get("price"))
        final = 0.70 * cos_score + 0.20 * age_score + 0.10 * price_score
        if final > best_score:
            best_score   = final
            best_product = p
    return best_product, best_score


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TRANSCRIPT FETCHING                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Language preference order: English first, then major Indian languages
_TRANSCRIPT_LANG_PRIORITY = ["en", "hi", "pa", "ta", "te", "kn", "ml", "bn", "or", "gu", "mr"]

# ── Transcript cache: persist fetched transcripts to avoid re-hitting YouTube ──
# Re-runs will load from this file instead of making new YouTube API calls.
_TRANSCRIPT_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcript_cache.json")
_transcript_cache: dict = {}
try:
    if os.path.exists(_TRANSCRIPT_CACHE_FILE):
        with open(_TRANSCRIPT_CACHE_FILE, "r", encoding="utf-8") as _tc:
            _transcript_cache = json.load(_tc)
        logger.info(f"Transcript cache loaded: {len(_transcript_cache)} cached videos.")
except Exception as _ce:
    logger.warning(f"Could not load transcript cache: {_ce}")


def _save_transcript_cache():
    try:
        with open(_TRANSCRIPT_CACHE_FILE, "w", encoding="utf-8") as _tc:
            json.dump(_transcript_cache, _tc, ensure_ascii=False, indent=2)
    except Exception as _e:
        logger.warning(f"Could not save transcript cache: {_e}")

def get_transcript(video_id):
    """
    Fetch transcript for video_id, trying English first then Indian regional languages.
    Results are cached in transcript_cache.json to avoid re-hitting YouTube on re-runs.
    IP-block failures are NOT cached permanently — they are retried on next run.
    Non-English transcripts are passed to Gemini which handles them natively.
    """
    # ── Cache hit: skip YouTube ──
    if video_id in _transcript_cache:
        cached_val = _transcript_cache[video_id]
        # Temporary IP block — always retry (don't trust cached block)
        if isinstance(cached_val, dict) and cached_val.get("__blocked__"):
            logger.info(f"  [{video_id}] Previously IP-blocked — retrying YouTube.")
            # Fall through to re-fetch below
        elif cached_val is None:
            logger.info(f"  [{video_id}] Transcript: permanently unavailable (cached).")
            return None
        else:
            logger.info(f"  [{video_id}] Transcript: loaded from cache ({len(cached_val)} chars).")
            return cached_val

    try:
        api = YouTubeTranscriptApi()
        # Try preferred languages in order
        try:
            transcript = api.fetch(video_id, languages=_TRANSCRIPT_LANG_PRIORITY)
            text = " ".join([entry.text for entry in transcript])
            if text.strip():
                _transcript_cache[video_id] = text
                _save_transcript_cache()
                return text
        except NoTranscriptFound:
            pass

        # Fallback: fetch whatever language is available
        try:
            transcript_list = api.list(video_id)
            for t in transcript_list:
                try:
                    fetched = t.fetch()
                    text = " ".join([entry.text for entry in fetched])
                    if text.strip():
                        logger.info(f"  Transcript found in '{t.language_code}' for {video_id}")
                        _transcript_cache[video_id] = text
                        _save_transcript_cache()
                        return text
                except Exception:
                    continue
        except Exception:
            pass

    except TranscriptsDisabled:
        # Permanent — cache as null
        logger.warning(f"  Transcripts disabled for {video_id}")
        _transcript_cache[video_id] = None
        _save_transcript_cache()
        return None
    except Exception as e:
        err = str(e)
        if "blocking" in err.lower() or "IPBlocked" in err or "RequestBlocked" in err or "blocked" in err.lower():
            # Temporary IP block — cache as blocked (will retry next run)
            logger.warning(f"  Transcript unavailable for {video_id}: YouTube IP block (will retry next run)")
            _transcript_cache[video_id] = {"__blocked__": True}
            _save_transcript_cache()
        else:
            # Other error — log and cache as permanent miss
            logger.warning(f"  Transcript unavailable for {video_id}: {e}")
            _transcript_cache[video_id] = None
            _save_transcript_cache()
        return None

    # Exhausted all language options with no result — permanent miss
    _transcript_cache[video_id] = None
    _save_transcript_cache()
    return None


def generate_fashion_from_context(creator_name, pincode, is_creator=True, store_name="Unknown"):
    """
    Fallback: when YouTube Shorts have no transcript, use Gemini to generate
    region-appropriate fashion items based on the creator/store context.
    """
    if not GEMINI_API_KEY:
        return []

    REGION_HINTS = {
        "800008": "Patna, Bihar — known for Banarasi silk, Bhagalpuri silk, Madhubani prints, "
                  "cotton kurtas, saffron outfits for Chhath Puja, wedding sherwanis, ethnic festive wear",
        "682001": "Kochi, Kerala — known for Kasavu sarees with gold zari, white and cream Kerala mundu, "
                  "cotton linen summer wear, pastel dresses, Vishu festival attire, boat-race casuals",
        "752001": "Odisha (Cuttack/Bhubaneswar) — known for Sambalpuri silk ikat weaves, Bomkai silk, "
                  "Pipli applique work, Tussar silk sarees, handloom cotton kurtas, temple motif prints",
    }
    region_hint = REGION_HINTS.get(pincode, f"Indian region pincode {pincode}")

    if is_creator:
        prompt = f"""
You are an AI fashion analyst. A local lifestyle content creator named "{creator_name}"
from {region_hint} (pincode {pincode}) creates fashion-related YouTube content.

Based on this creator's probable style for their region, generate exactly 3 DISTINCT
clothing items they would likely showcase. Use authentic regional fashion knowledge.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "maroon silk Banarasi saree",
    "description": "Heavy pure silk Banarasi saree with intricate gold zari brocade, ideal for wedding ceremonies.",
    "tags": ["silk", "banarasi", "festive", "ethnic", "traditional", "ceremonial"],
    "aesthetic": "festive ethnic bridal",
    "material": "pure silk",
    "fabric": "silk",
    "color": "maroon",
    "age_group": "25-35",
    "estimated_price_inr": 8500,
    "occasion": "wedding"
  }}
]
"""
    else:
        prompt = f"""
You are an AI retail fashion analyst. A local boutique/store named "{store_name}"
located in {region_hint} (pincode {pincode}) features regional fashion inventory.

Based on what this store would likely carry, generate exactly 3 DISTINCT clothing items.
Use authentic regional fashion knowledge.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "green Kasavu saree",
    "description": "Traditional Kerala handloom saree woven with thick gold zari border, perfect for Onam.",
    "tags": ["kasavu", "handloom", "traditional", "ethnic", "kerala"],
    "aesthetic": "traditional Kerala ethnic",
    "material": "handloom cotton",
    "fabric": "cotton",
    "color": "white and gold",
    "age_group": "25-45",
    "estimated_price_inr": 2200,
    "inventory_status": "new arrival"
  }}
]
"""

    try:
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        dresses = json.loads(text)
        return dresses[:MAX_DRESSES] if isinstance(dresses, list) else []
    except Exception as e:
        logger.error(f"  Gemini context-based generation failed: {e}")
        return []


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GEMINI GARMENT EXTRACTION                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def extract_dresses_from_transcript(transcript_text, is_creator=True, pincode="800008"):
    """
    Sends the transcript to Gemini and extracts 2-3 distinct garment descriptions
    each with a full product-level schema.
    """
    if not GEMINI_API_KEY or not transcript_text:
        return []

    if is_creator:
        prompt = f"""
You are an AI fashion extractor. Read this video transcript from a local lifestyle creator.
Identify exactly 2 or 3 DISTINCT clothing items or outfits being shown or discussed.
For EACH garment fill in ALL fields below. Use your fashion knowledge to estimate age_group and price.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "maroon silk Banarasi saree",
    "description": "Heavy pure silk Banarasi saree with intricate gold zari brocade, ideal for wedding ceremonies.",
    "tags": ["silk", "banarasi", "festive", "ethnic", "traditional", "ceremonial"],
    "aesthetic": "festive ethnic bridal",
    "material": "pure silk",
    "fabric": "silk",
    "color": "maroon",
    "age_group": "25-35",
    "estimated_price_inr": 8500,
    "occasion": "wedding"
  }}
]

Transcript (pincode {pincode}):
{transcript_text[:3000]}
"""
    else:
        prompt = f"""
You are an AI retail inventory extractor. Read this transcript from a local boutique store tour.
Identify exactly 2 or 3 DISTINCT clothing items on display.
For EACH garment fill in ALL fields below. Use your fashion knowledge to estimate age_group and price.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "green Kasavu saree",
    "description": "Traditional Kerala handloom saree woven with thick gold zari border, perfect for Onam.",
    "tags": ["kasavu", "handloom", "traditional", "ethnic", "kerala"],
    "aesthetic": "traditional Kerala ethnic",
    "material": "handloom cotton",
    "fabric": "cotton",
    "color": "white and gold",
    "age_group": "25-45",
    "estimated_price_inr": 2200,
    "inventory_status": "new arrival"
  }}
]

Transcript (pincode {pincode}):
{transcript_text[:3000]}
"""

    try:
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        dresses = json.loads(text)
        return dresses[:MAX_DRESSES] if isinstance(dresses, list) else []
    except Exception as e:
        logger.error(f"  Gemini extraction failed: {e}")
        return []


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                           MAIN SEEDER                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def process_seeding_from_excel(excel_path):
    if not os.path.exists(excel_path):
        logger.error(f"Excel file not found: {excel_path}")
        return

    logger.info(f"Loading seed inputs from: {excel_path}")
    df = pd.read_excel(excel_path)
    catalog = load_catalog()
    logger.info(f"Catalog loaded: {len(catalog)} Myntra products")
    logger.info(f"Hybrid scoring: 70% cosine | 20% age range | 10% price ratio\n")

    all_records   = []
    dress_counter = 0

    for row_idx, (_, row) in enumerate(df.iterrows()):
        video_id   = str(row.get("video_id", "")).strip()
        pincode    = str(row.get("pincode", "800008")).strip()
        feed_type  = str(row.get("type", "creator")).strip().lower()
        store_name = str(row.get("store_name", "Unknown")).strip()

        if not video_id or video_id == "nan":
            continue

        # Inter-video delay to avoid YouTube rate-limiting.
        # Skip delay on the first video, and also skip if the transcript is cached.
        if row_idx > 0 and video_id not in _transcript_cache:
            import time
            time.sleep(3)

        logger.info(f"\n  Processing ({feed_type}) Video ID: {video_id}  [{pincode}]")

        # 1. Transcript
        is_creator = (feed_type == "creator")
        transcript = get_transcript(video_id)

        # Initialise transcript_dresses for use in multi-query path
        transcript_dresses = []

        if transcript:
            # 2a. Transcript available → extract from transcript
            transcript_dresses = extract_dresses_from_transcript(transcript, is_creator, pincode)
            logger.info(f"  Gemini (transcript): {len(transcript_dresses)} garments extracted.")
        else:
            # 2b. No transcript (YouTube Shorts / music-only) —
            #     Try CLIP thumbnail classification FIRST (new path).
            logger.info(f"  No transcript — attempting CLIP thumbnail classification.")
            clip_meta = classify_thumbnail_with_clip(video_id)
            if clip_meta:
                transcript_dresses = [clip_meta]
                logger.info(f"  CLIP: garment '{clip_meta['item']}' detected from thumbnail.")
            else:
                # CLIP also failed — fall back to Gemini regional-context generator.
                logger.info(f"  CLIP unavailable — falling back to Gemini context generation.")
                transcript_dresses = generate_fashion_from_context(store_name, pincode, is_creator, store_name)
                logger.info(f"  Gemini (context): {len(transcript_dresses)} garments generated.")

        # 3. Multi-query RRF: fuse transcript + thumbnail + regional-prior ranked lists.
        #    Returns the single best catalog match and metadata about which paths fired.
        best, rrf_score, query_sources = find_best_match_multi_query(
            video_id=video_id,
            transcript_dresses=transcript_dresses,
            catalog=catalog,
            zip_code=pincode,
        )

        matched_id   = best.get("id")   if best else None
        matched_name = best.get("name") if best else None

        if best:
            logger.info(
                f"  └─ RRF match: '{matched_name}'  "
                f"(rrf={rrf_score:.4f}, sources={query_sources})"
            )
        else:
            logger.info(f"  └─ no catalog match found.")

        # 4. Per garment: build individual records (one per extracted garment)
        #    Each record points to the same RRF-selected best match but keeps its
        #    individual Gemini/CLIP metadata for the frontend.
        for dress_idx, d in enumerate(transcript_dresses):
            dress_counter += 1
            item_name    = d.get("item", "Unknown")
            dress_vector = embed_dress(d)

            age_s   = age_overlap_score(
                d.get("age_group", ""),
                best.get("age_group", "") if best else "",
            )
            price_s = price_proximity_score(
                d.get("estimated_price_inr"),
                best.get("price") if best else None,
            )

            logger.info(
                f"    Garment {dress_idx+1}: '{item_name}'  "
                f"[age={d.get('age_group')} / ₹{d.get('estimated_price_inr')}]"
            )

            record = {
                "id":                    f"{pincode}_{feed_type}_{video_id}_{dress_counter}",
                "type":                  feed_type,
                "pincode":               pincode,
                "video_id":              video_id,
                "metadata":              d,
                "vector":                dress_vector,
                "matched_product_id":    matched_id,
                "matched_product_name":  matched_name,
                # RRF score replaces the old single-query hybrid_score.
                # Kept under the same key so downstream consumers are unchanged.
                "hybrid_score":          round(rrf_score, 4) if best else 0.0,
                "rrf_score":             round(rrf_score, 4) if best else 0.0,
                "query_sources":         query_sources,
                "age_overlap_score":     round(age_s, 4),
                "price_proximity_score": round(price_s, 4),
            }
            if not is_creator:
                record["store_name"] = d.get("store_name", store_name)

            all_records.append(record)

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=4)

    logger.info(f"\n{'='*60}")
    logger.info(f"  Seeding complete!")
    logger.info(f"  {len(all_records)} garment records → {OUTPUT_FILE}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    excel_input = sys.argv[1] if len(sys.argv) > 1 else "pinpulse_youtube_seed.xlsx"
    process_seeding_from_excel(excel_input)
