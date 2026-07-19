"""
PinPulse Mock Database Seeder  (HACKATHON — Local JSON Cache)
=============================================================
Triggered when a team member uploads pinpulse_youtube_seed.xlsx.

Architecture per Excel row:
  1. YouTubeTranscriptApi  →  full transcript text
  2. Gemini LLM            →  extract 2-3 garments with FULL product schema:
                               item, description, tags, aesthetic, material,
                               fabric, color, age_group, estimated_price_inr,
                               occasion / inventory_status
  3. embed_dress()         →  512-dim vector from TEXT fields only
                               (excludes age_group and estimated_price_inr)
  4. find_best_catalog_match()  →  HYBRID scoring:
                               - 70% cosine similarity on embedding
                               - 20% age_group range overlap  (range comparison)
                               - 10% price proximity           (ratio decay)
  5. JSON export           →  appends all garment + match records to pinpulse_mock_db.json

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

sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector

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
    return get_vibe_vector(tags=all_tags, category_str=category, aesthetic_str=aesthetic)


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

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        logger.error(f"  Failed to fetch transcript for {video_id}: {e}")
        return None


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

    for _, row in df.iterrows():
        video_id   = str(row.get("video_id", "")).strip()
        pincode    = str(row.get("pincode", "800008")).strip()
        feed_type  = str(row.get("type", "creator")).strip().lower()
        store_name = str(row.get("store_name", "Unknown")).strip()

        if not video_id or video_id == "nan":
            continue

        logger.info(f"\n  Processing ({feed_type}) Video ID: {video_id}  [{pincode}]")

        # 1. Transcript
        transcript = get_transcript(video_id)
        if not transcript:
            continue

        # 2. Gemini: 2-3 full-schema garments
        is_creator = (feed_type == "creator")
        dresses = extract_dresses_from_transcript(transcript, is_creator, pincode)
        logger.info(f"  Gemini: {len(dresses)} garments extracted.")

        # 3. Per garment: text embedding → hybrid match → build record
        for d in dresses:
            dress_counter += 1
            item_name    = d.get("item", "Unknown")
            dress_vector = embed_dress(d)
            best, score  = find_best_catalog_match(dress_vector, d, catalog, pincode)

            matched_id   = best.get("id")   if best else None
            matched_name = best.get("name") if best else None

            age_s   = age_overlap_score(d.get("age_group",""), best.get("age_group","") if best else "")
            price_s = price_proximity_score(d.get("estimated_price_inr"), best.get("price") if best else None)

            logger.info(f"    Garment: '{item_name}'  [age={d.get('age_group')} / ₹{d.get('estimated_price_inr')}]")
            if best:
                logger.info(f"    └─ '{matched_name}'  (hybrid={score:.4f}  age={age_s:.2f}  price={price_s:.2f})")
            else:
                logger.info(f"    └─ no catalog match found.")

            record = {
                "id":                   f"{pincode}_{feed_type}_{video_id}_{dress_counter}",
                "type":                 feed_type,
                "pincode":              pincode,
                "video_id":             video_id,
                "metadata":             d,
                "vector":               dress_vector,
                "matched_product_id":   matched_id,
                "matched_product_name": matched_name,
                "hybrid_score":         round(score, 4) if best else 0.0,
                "age_overlap_score":    round(age_s, 4),
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
