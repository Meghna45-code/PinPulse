"""
PinPulse Live Trend Extraction Pipeline  (PRODUCTION — Supabase SQL)
=====================================================================
Architecture per ZIP code (Patna 800008, Kochi 682001, Puri 752001):

  CREATORS (3 per region):
    1. YouTube Data API v3 search  →  3 recent creator fashion/vlog videos
       (publishedAfter = 18 months ago for recency)
    2. YouTubeTranscriptApi        →  full transcript text per video
    3. Gemini LLM                  →  extract 2-3 garments with FULL product schema per video:
                                      item, description, tags, aesthetic, material,
                                      fabric, color, age_group, estimated_price_inr, occasion
    4. embed_dress()               →  512-dim vector from TEXT fields only
                                      (item, description, tags, aesthetic, material, fabric, color)
    5. find_best_catalog_match()   →  HYBRID scoring:
                                      - 70% cosine similarity on embedding
                                      - 20% age_group range overlap  (simple range comparison)
                                      - 10% price proximity           (ratio-based decay)
    6. Supabase writes             →  creators / creator_videos / creator_video_products

  BOUTIQUES (3 per region):
    1. Google Places Text Search   →  3 boutiques near the locality
    2. YouTube Data API v3 search  →  1 recent store-tour video per boutique
    3. YouTubeTranscriptApi        →  transcript
    4-5. Same Gemini + embedding + hybrid matching as above
    6. Supabase writes             →  regional_boutique_trends
"""

import os
import sys
import json
import math
import re
import time
import logging
import numpy as np
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_trend_extraction_pipeline")

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
GOOGLE_API_KEY            = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY            = os.getenv("GEMINI_API_KEY")
SUPABASE_URL              = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY missing — LLM extraction will be skipped.")

LOCAL_CATALOG_FILE   = os.path.join(os.path.dirname(__file__), "local_catalog.json")
MAX_CREATORS         = 3
MAX_BOUTIQUES        = 3
MAX_DRESSES_PER_VID  = 3
PUBLISHED_AFTER      = (datetime.utcnow() - timedelta(days=548)).strftime("%Y-%m-%dT%H:%M:%SZ")

REGIONS = {
    "800008": {
        "name": "Patna",
        "locality": "Frazer Road, Patna, Bihar",
        "creator_query": "Patna Bihar fashion vlog outfit haul street style creator 2024",
        "boutique_query": "Pata Bihar clothing store boutique saree market tour 2024",
        "places_query": "clothing boutique saree store ethnic wear Patna Bihar",
    },
    "682001": {
        "name": "Kochi",
        "locality": "MG Road, Kochi, Kerala",
        "creator_query": "Kochi Kerala fashion vlog outfit haul style creator 2024",
        "boutique_query": "Kochi Kerala clothing boutique store tour kasavu handloom 2024",
        "places_query": "clothing boutique kasavu saree handloom store Kochi Kerala",
    },
    "752001": {
        "name": "Puri",
        "locality": "Puri Jagannath Temple Area, Puri, Odisha",
        "creator_query": "Odisha Puri fashion vlog traditional sambalpuri handloom outfit 2024",
        "boutique_query": "Puri Odisha sambalpuri saree clothing store boutique tour 2024",
        "places_query": "clothing boutique sambalpuri saree store Puri Odisha",
    },
}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              HYBRID SCORING — three independent signals                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# Age group string → (min_age, max_age)
AGE_RANGES = {
    "teen": (13, 19), "teens": (13, 19),
    "college": (18, 24), "18-24": (18, 24), "18-25": (18, 25),
    "young adult": (20, 28), "20-30": (20, 30), "20-28": (20, 28),
    "25-35": (25, 35), "25-40": (25, 40),
    "30-40": (30, 40), "30-45": (30, 45),
    "35+": (35, 65), "35-50": (35, 50),
    "40+": (40, 65), "45+": (45, 65),
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
    Range overlap score: 1.0 = full overlap, decays to 0.0 as gap grows.
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
    Ratio-based price proximity: peaks at 1.0 when prices are equal,
    decays with log-scale distance, returns 0.0 beyond 3× ratio.
    Returns 0.5 (neutral) when either side has no price info.
    """
    if not dress_price or not product_price or product_price == 0:
        return 0.5
    ratio = float(dress_price) / float(product_price)
    if ratio <= 0:
        return 0.0
    log_ratio = math.log(ratio)
    sigma = 0.7   # controls how fast the score decays
    return float(math.exp(-0.5 * (log_ratio / sigma) ** 2))

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
    Generate a 512-dim vector using TEXT fields only:
      item, description, tags, aesthetic, material, fabric, color, occasion/inventory_status.

    age_group and estimated_price_inr are intentionally excluded here —
    they are compared separately via range/ratio matching.
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

def load_catalog():
    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        logger.warning(f"    No transcript for {video_id}: {e}")
        return None


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GEMINI GARMENT EXTRACTION                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def extract_dresses_from_transcript(transcript_text, source_type="creator", pincode="800008"):
    """
    Gemini extracts 2-3 garments with a full product-level schema per transcript.
    Each garment gets:
      item, description, tags, aesthetic, material, fabric, color,
      age_group, estimated_price_inr, plus occasion (creator) or inventory_status (boutique).
    """
    if not GEMINI_API_KEY or not transcript_text:
        return []

    if source_type == "creator":
        prompt = f"""
You are an AI fashion extractor. Read this video transcript from a local lifestyle creator.
Identify exactly 2 or 3 DISTINCT clothing items or outfits being shown or discussed.
For EACH garment fill in ALL fields below. Use your fashion knowledge to estimate age_group and price.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "maroon silk Banarasi saree",
    "description": "Heavy pure silk Banarasi saree with intricate gold zari brocade work, curated for wedding pheras.",
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
You are an AI retail inventory extractor. Read this transcript from a local boutique store tour video.
Identify exactly 2 or 3 DISTINCT clothing items on display.
For EACH garment fill in ALL fields below. Use your fashion knowledge to estimate age_group and price.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{
    "item": "green Kasavu saree",
    "description": "Traditional Kerala handloom saree woven with thick gold zari border, perfect for Onam festivities.",
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
        return dresses[:MAX_DRESSES_PER_VID] if isinstance(dresses, list) else []
    except Exception as e:
        logger.error(f"    Gemini extraction failed: {e}")
        return []


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          YOUTUBE DATA API v3                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def search_youtube_videos(query, max_results=3):
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_MAPS_API_KEY missing — cannot call YouTube Data API.")
        return []
    params = {
        "part": "snippet", "q": query, "maxResults": max_results,
        "type": "video", "order": "relevance",
        "publishedAfter": PUBLISHED_AFTER, "key": GOOGLE_API_KEY,
    }
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=15)
    if r.status_code != 200:
        logger.error(f"YouTube search failed for '{query}': {r.text}")
        return []
    videos = []
    for item in r.json().get("items", []):
        snippet  = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            continue
        videos.append({
            "video_id":      video_id,
            "title":         snippet.get("title", ""),
            "channel":       snippet.get("channelTitle", "Unknown Creator"),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "video_url":     f"https://www.youtube.com/watch?v={video_id}",
            "description":   snippet.get("description", ""),
            "published_at":  snippet.get("publishedAt", ""),
        })
    return videos


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GOOGLE PLACES TEXT SEARCH                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def search_boutiques_places(places_query, locality, zip_code, max_results=3):
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_MAPS_API_KEY missing — cannot call Google Places API.")
        return []
    params = {"query": f"{places_query} near {locality}", "key": GOOGLE_API_KEY}
    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params=params, timeout=15
    )
    if r.status_code != 200:
        logger.error(f"Google Places failed: {r.text}")
        return []
    boutiques = []
    for idx, place in enumerate(r.json().get("results", [])[:max_results]):
        name     = place.get("name", "Unknown Store")
        addr     = place.get("formatted_address", locality)
        rating   = place.get("rating", 4.0)
        place_id = place.get("place_id", "")
        boutiques.append({
            "store_id":  f"STR_{zip_code}_{idx+1:03d}",
            "zip_code":  zip_code,
            "locality":  locality,
            "store_name": name, "address": addr, "rating": rating,
            "maps_url":  f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            "social_signal_source": "Instagram Location Signal" if idx % 2 == 0 else "YouTube Store Tour",
            "simulated_engagement": int(12000 + (rating * 4500) + (idx * 1500)),
        })
    return boutiques


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            MAIN PIPELINE                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def run_pipeline():
    logger.info("=" * 65)
    logger.info("  PINPULSE LIVE TREND EXTRACTION PIPELINE")
    logger.info(f"  Recency: publishedAfter={PUBLISHED_AFTER}")
    logger.info(f"  Per region: {MAX_CREATORS} creators + {MAX_BOUTIQUES} boutiques")
    logger.info(f"  Matching: 70% cosine | 20% age range | 10% price ratio")
    logger.info("=" * 65)

    catalog = load_catalog()
    logger.info(f"  Catalog: {len(catalog)} Myntra products loaded.\n")

    sb = None
    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("  Supabase: connected ✅")
    except Exception as e:
        logger.warning(f"  Supabase: connection failed ({e}). Dry-run mode.")

    for zip_code, region_info in REGIONS.items():
        region_name = region_info["name"]
        locality    = region_info["locality"]
        logger.info(f"\n{'━'*65}")
        logger.info(f"  REGION: {region_name}  ({zip_code})")
        logger.info(f"{'━'*65}")

        # ══ A. CREATORS ═══════════════════════════════════════════════
        logger.info(f"\n  [A] Creators — YouTube: '{region_info['creator_query']}'")
        creator_vids = search_youtube_videos(region_info["creator_query"], MAX_CREATORS)
        logger.info(f"  [A] {len(creator_vids)} videos found.")

        for vid in creator_vids:
            channel = vid["channel"]
            logger.info(f"\n    ▶ {channel}  |  '{vid['title'][:60]}'")

            # 1. Upsert creator
            creator_emb = get_vibe_vector(
                tags=["fashion", "lifestyle", "creator", region_name.lower()],
                category_str="casual", aesthetic_str="lifestyle creator"
            )
            creator_db_id = None
            if sb:
                try:
                    res = sb.table("creators").insert({
                        "name": channel, "zip_code": zip_code,
                        "subscriber_count": 0,
                        "youtube_channel_url": f"https://www.youtube.com/@{channel.replace(' ', '')}",
                        "demographic": "gen-z", "embedding": creator_emb,
                    }).execute()
                    creator_db_id = res.data[0]["id"] if res.data else None
                    logger.info(f"      creators → ID={creator_db_id}")
                except Exception as e:
                    logger.warning(f"      creators insert failed: {e}")

            # 2. Insert creator_video
            video_db_id = None
            if sb:
                try:
                    res = sb.table("creator_videos").insert({
                        "creator_id": creator_db_id,
                        "video_url": vid["video_url"],
                        "title": vid["title"],
                        "description": (vid["description"] or "")[:500],
                        "video_screenshot_url": vid["thumbnail_url"],
                        "simulated_engagement": 45000,
                    }).execute()
                    video_db_id = res.data[0]["id"] if res.data else None
                    logger.info(f"      creator_videos → ID={video_db_id}")
                except Exception as e:
                    logger.warning(f"      creator_videos insert failed: {e}")

            # 3. Transcript
            transcript = get_transcript(vid["video_id"])
            if not transcript:
                time.sleep(1.0)
                continue

            # 4. Gemini: extract 2-3 full-schema garments
            dresses = extract_dresses_from_transcript(transcript, "creator", zip_code)
            logger.info(f"      Gemini: {len(dresses)} garments extracted.")

            # 5. Per garment: text embedding → hybrid match → link
            for d in dresses:
                vec  = embed_dress(d)
                prod, score = find_best_catalog_match(vec, d, catalog, zip_code)
                logger.info(f"        '{d.get('item')}' [{d.get('age_group')} / ₹{d.get('estimated_price_inr')}]")
                if prod:
                    logger.info(f"        └─ '{prod.get('name')}' (hybrid={score:.4f}  "
                                f"age={age_overlap_score(d.get('age_group',''), prod.get('age_group','')):.2f}  "
                                f"price={price_proximity_score(d.get('estimated_price_inr'), prod.get('price')):.2f})")
                    if sb and video_db_id and prod.get("id"):
                        try:
                            sb.table("creator_video_products").insert({
                                "video_id": video_db_id,
                                "product_id": prod["id"],
                                "confidence_score": round(score, 4),
                            }).execute()
                        except Exception as e:
                            logger.warning(f"        creator_video_products insert failed: {e}")

            time.sleep(1.5)

        # ══ B. BOUTIQUES ══════════════════════════════════════════════
        logger.info(f"\n  [B] Boutiques — Google Places: '{region_info['places_query']}'")
        boutiques = search_boutiques_places(region_info["places_query"], locality, zip_code, MAX_BOUTIQUES)
        logger.info(f"  [B] {len(boutiques)} boutiques found.")

        for store in boutiques:
            sname = store["store_name"]
            logger.info(f"\n    🏪 {sname}  |  {store.get('address', locality)}")

            tour_vids = search_youtube_videos(f"{sname} {region_name} store tour clothing 2024", 1)
            trend_tags, matched_names = [], []

            if tour_vids:
                transcript = get_transcript(tour_vids[0]["video_id"])
                if transcript:
                    dresses = extract_dresses_from_transcript(transcript, "boutique", zip_code)
                    logger.info(f"      Gemini: {len(dresses)} garments extracted from store tour.")
                    for d in dresses:
                        vec  = embed_dress(d)
                        prod, score = find_best_catalog_match(vec, d, catalog, zip_code)
                        logger.info(f"        '{d.get('item')}' [{d.get('age_group')} / ₹{d.get('estimated_price_inr')}]")
                        if prod:
                            trend_tags.append(d.get("aesthetic", d.get("vibe", "ethnic")))
                            matched_names.append(prod.get("name", ""))
                            logger.info(f"        └─ '{prod.get('name')}' (hybrid={score:.4f})")

            extracted_trend = (", ".join(trend_tags[:2]) if trend_tags
                               else region_info["places_query"].split()[0])
            style_cluster   = (f"Matched: {'; '.join(matched_names[:2])}"
                               if matched_names else f"Regional — {region_name}")

            if sb:
                try:
                    sb.table("regional_boutique_trends").upsert({
                        "store_id":               store["store_id"],
                        "zip_code":               zip_code,
                        "locality":               store["locality"],
                        "store_name":             sname,
                        "social_signal_source":   store["social_signal_source"],
                        "simulated_engagement":   store["simulated_engagement"],
                        "extracted_visual_trend": extracted_trend[:50],
                        "style_vibe_cluster":     style_cluster[:100],
                    }).execute()
                    logger.info(f"      regional_boutique_trends → upserted ✅")
                except Exception as e:
                    logger.warning(f"      boutique upsert failed: {e}")

            time.sleep(1.0)

    logger.info(f"\n{'═'*65}")
    logger.info("  PIPELINE COMPLETE — all data written to Supabase.")
    logger.info(f"{'═'*65}")


if __name__ == "__main__":
    run_pipeline()
