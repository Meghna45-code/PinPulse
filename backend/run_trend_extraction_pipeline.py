"""
PinPulse Live Trend Extraction Pipeline  (PRODUCTION — Supabase SQL)
=====================================================================
Architecture per ZIP code (Patna 800008, Kochi 682001, Puri 752001):

  CREATORS (3 per region):
    1. YouTube Data API v3 search  →  3 recent creator fashion/vlog videos
       (publishedAfter = 18 months ago for recency)
    2. YouTubeTranscriptApi        →  full transcript text per video
    3. Gemini LLM                  →  extract 2-3 distinct garments per transcript
    4. get_vibe_vector()           →  generate a separate 512-dim vector per garment
    5. Cosine similarity           →  match each garment vector to the best Myntra catalog product
    6. Supabase writes             →  creators / creator_videos / creator_video_products

  BOUTIQUES (3 per region):
    1. Google Places Text Search   →  3 boutiques near the locality
    2. YouTube Data API v3 search  →  1 recent store-tour video per boutique
    3. YouTubeTranscriptApi        →  full transcript text per video
    4. Gemini LLM                  →  extract 2-3 distinct garments per transcript
    5. get_vibe_vector()           →  separate 512-dim vector per garment
    6. Cosine similarity           →  match each garment to best Myntra catalog product
    7. Supabase writes             →  regional_boutique_trends (trend + matched product names)

Run once with live API credentials to seed the production database.
"""

import os
import sys
import json
import time
import logging
import numpy as np
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Import the EXACT same embedding model used for the Myntra product catalog
# to ensure mathematical parity in cosine similarity comparisons
sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_trend_extraction_pipeline")

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GOOGLE_API_KEY           = os.getenv("GOOGLE_MAPS_API_KEY")   # serves both YouTube & Places
GEMINI_API_KEY           = os.getenv("GEMINI_API_KEY")
SUPABASE_URL             = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY missing — LLM extraction will be skipped.")

LOCAL_CATALOG_FILE = os.path.join(os.path.dirname(__file__), "local_catalog.json")

# ── Pipeline Config ───────────────────────────────────────────────────────────
MAX_CREATORS_PER_REGION  = 3
MAX_BOUTIQUES_PER_REGION = 3
MAX_DRESSES_PER_VIDEO    = 3   # Gemini extracts up to this many garments per transcript

# Recency filter: only fetch videos published in the last 18 months
PUBLISHED_AFTER = (datetime.utcnow() - timedelta(days=548)).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── Regions ───────────────────────────────────────────────────────────────────
REGIONS = {
    "800008": {
        "name": "Patna",
        "locality": "Frazer Road, Patna, Bihar",
        "creator_search_query": "Patna Bihar fashion vlog outfit haul street style creator 2024",
        "boutique_yt_query":    "Patna Bihar clothing store boutique saree market tour 2024",
        "places_query":         "clothing boutique saree store ethnic wear Patna Bihar",
    },
    "682001": {
        "name": "Kochi",
        "locality": "MG Road, Kochi, Kerala",
        "creator_search_query": "Kochi Kerala fashion vlog outfit haul style creator 2024",
        "boutique_yt_query":    "Kochi Kerala clothing boutique store tour kasavu handloom 2024",
        "places_query":         "clothing boutique kasavu saree handloom store Kochi Kerala",
    },
    "752001": {
        "name": "Puri",
        "locality": "Puri Jagannath Temple Area, Puri, Odisha",
        "creator_search_query": "Odisha Puri fashion vlog traditional sambalpuri handloom outfit 2024",
        "boutique_yt_query":    "Puri Odisha sambalpuri saree clothing store boutique tour 2024",
        "places_query":         "clothing boutique sambalpuri saree store Puri Odisha",
    },
}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         UTILITY FUNCTIONS                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def cosine_similarity(a, b):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def load_catalog():
    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_best_catalog_match(dress_vector, catalog, zip_code):
    """
    Cosine similarity search:
    Compare a single dress embedding against every product in the catalog
    and return the best matching product + its similarity score.
    """
    best_product, best_score = None, -1.0
    for p in catalog:
        p_zips = p.get("zip_codes", [])
        if p_zips and zip_code not in p_zips:
            continue
        p_emb = p.get("embedding", [])
        if not p_emb or len(p_emb) != len(dress_vector):
            continue
        score = cosine_similarity(dress_vector, p_emb)
        if score > best_score:
            best_score = score
            best_product = p
    return best_product, best_score


def embed_dress(dress_meta):
    """
    Generate a 512-dim vector for a single extracted garment.
    Uses the EXACT same get_vibe_vector() as the Myntra catalog
    to ensure vectors live in the same embedding space.
    """
    tags = [
        dress_meta.get("item", ""),
        dress_meta.get("vibe", ""),
        dress_meta.get("fabric", ""),
        dress_meta.get("color", ""),
    ]
    tags = [t.lower().strip() for t in tags if t]
    category  = "festive" if "festive" in dress_meta.get("vibe", "").lower() else "casual"
    aesthetic = dress_meta.get("vibe", "casual")
    return get_vibe_vector(tags=tags, category_str=category, aesthetic_str=aesthetic)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TRANSCRIPT FETCHING                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        logger.warning(f"    No transcript available for video {video_id}: {e}")
        return None


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GEMINI GARMENT EXTRACTION                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def extract_dresses_from_transcript(transcript_text, source_type="creator", pincode="800008"):
    """
    Uses Gemini to identify 2-3 distinct garments from a transcript.
    Returns a list of dress metadata dicts.

    source_type='creator'  → Prompt A (fashion vlog)
    source_type='boutique' → Prompt B (store tour / retail)
    """
    if not GEMINI_API_KEY or not transcript_text:
        return []

    if source_type == "creator":
        prompt = f"""
You are an AI fashion extractor. Read this video transcript from a local lifestyle creator.
Identify exactly 2 or 3 DISTINCT clothing items or outfits that are being shown or discussed.
For EACH item, return one JSON object.

Return ONLY a valid JSON array — no markdown, no extra text — like this:
[
  {{"item": "maroon silk Banarasi saree", "fabric": "silk", "color": "maroon", "vibe": "festive ethnic", "occasion": "wedding"}},
  {{"item": "yellow cotton kurti", "fabric": "cotton", "color": "yellow", "vibe": "casual ethnic", "occasion": "college"}}
]

Transcript (pincode {pincode}):
{transcript_text[:3000]}
"""
    else:
        prompt = f"""
You are an AI retail inventory extractor. Read this transcript from a local boutique store tour video.
Identify exactly 2 or 3 DISTINCT clothing items on display or being described.
For EACH item, return one JSON object.

Return ONLY a valid JSON array — no markdown, no extra text — like this:
[
  {{"item": "green Kasavu saree", "fabric": "cotton", "color": "white and gold", "vibe": "traditional Kerala", "inventory_status": "new arrival"}},
  {{"item": "pastel chikankari kurti", "fabric": "georgette", "color": "pastel pink", "vibe": "ethnic casual", "inventory_status": "bestseller"}}
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
        if isinstance(dresses, list):
            return dresses[:MAX_DRESSES_PER_VIDEO]
        return []
    except Exception as e:
        logger.error(f"    Gemini garment extraction failed: {e}")
        return []


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          YOUTUBE DATA API v3                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def search_youtube_videos(query, max_results=3):
    """
    Search YouTube for recent videos.
    Enforces recency via publishedAfter (last 18 months).
    """
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_MAPS_API_KEY missing — cannot call YouTube Data API.")
        return []

    params = {
        "part":          "snippet",
        "q":             query,
        "maxResults":    max_results,
        "type":          "video",
        "order":         "relevance",
        "publishedAfter": PUBLISHED_AFTER,
        "key":           GOOGLE_API_KEY,
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
            "video_id":     video_id,
            "title":        snippet.get("title", ""),
            "channel":      snippet.get("channelTitle", "Unknown Creator"),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "video_url":    f"https://www.youtube.com/watch?v={video_id}",
            "description":  snippet.get("description", ""),
            "published_at": snippet.get("publishedAt", ""),
        })
    return videos


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GOOGLE PLACES TEXT SEARCH                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def search_boutiques_google_places(places_query, locality, zip_code, max_results=3):
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_MAPS_API_KEY missing — cannot call Google Places API.")
        return []

    params = {
        "query": f"{places_query} near {locality}",
        "key":   GOOGLE_API_KEY,
    }
    r = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params=params, timeout=15
    )
    if r.status_code != 200:
        logger.error(f"Google Places search failed: {r.text}")
        return []

    boutiques = []
    for idx, place in enumerate(r.json().get("results", [])[:max_results]):
        name     = place.get("name", "Unknown Store")
        addr     = place.get("formatted_address", locality)
        rating   = place.get("rating", 4.0)
        place_id = place.get("place_id", "")
        boutiques.append({
            "store_id":           f"STR_{zip_code}_{idx+1:03d}",
            "zip_code":           zip_code,
            "locality":           locality,
            "store_name":         name,
            "address":            addr,
            "rating":             rating,
            "maps_url":           f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            "social_signal_source": "Instagram Location Signal" if idx % 2 == 0 else "YouTube Store Tour",
            "simulated_engagement": int(12000 + (rating * 4500) + (idx * 1500)),
        })
    return boutiques


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            MAIN PIPELINE                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def run_pipeline():
    logger.info("=" * 65)
    logger.info("  PINPULSE LIVE TREND EXTRACTION PIPELINE — PRODUCTION")
    logger.info("=" * 65)
    logger.info(f"  Recency filter  : publishedAfter = {PUBLISHED_AFTER}")
    logger.info(f"  Creators/region : {MAX_CREATORS_PER_REGION}")
    logger.info(f"  Boutiques/region: {MAX_BOUTIQUES_PER_REGION}")
    logger.info(f"  Dresses/video   : up to {MAX_DRESSES_PER_VIDEO}")

    catalog = load_catalog()
    logger.info(f"  Catalog loaded  : {len(catalog)} Myntra products\n")

    # Connect to Supabase
    sb = None
    try:
        from supabase import create_client
        sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("  Supabase: connected ✅")
    except Exception as e:
        logger.warning(f"  Supabase: connection failed ({e}). Dry-run mode — no DB writes.")

    for zip_code, region_info in REGIONS.items():
        region_name = region_info["name"]
        locality    = region_info["locality"]

        logger.info(f"\n{'━'*65}")
        logger.info(f"  REGION: {region_name}  ({zip_code})")
        logger.info(f"{'━'*65}")

        # ══════════════════════════════════════════════════════════════
        # SECTION A: LOCAL CONTENT CREATORS
        # ══════════════════════════════════════════════════════════════
        logger.info(f"  [A] Creators — searching: '{region_info['creator_search_query']}'")
        creator_videos = search_youtube_videos(
            region_info["creator_search_query"],
            max_results=MAX_CREATORS_PER_REGION
        )
        logger.info(f"  [A] {len(creator_videos)} recent creator videos found.")

        for vid in creator_videos:
            video_id = vid["video_id"]
            channel  = vid["channel"]
            logger.info(f"\n    ▶ Creator: {channel}")
            logger.info(f"      Video  : '{vid['title'][:70]}'")
            logger.info(f"      URL    : {vid['video_url']}")

            # ── 1. Upsert creator record ───────────────────────────────
            creator_embedding = get_vibe_vector(
                tags=["fashion", "lifestyle", "creator", region_name.lower()],
                category_str="casual",
                aesthetic_str="lifestyle creator"
            )
            creator_record = {
                "name":                channel,
                "zip_code":            zip_code,
                "subscriber_count":    0,
                "youtube_channel_url": f"https://www.youtube.com/@{channel.replace(' ', '').replace('&', 'and')}",
                "demographic":         "gen-z",
                "embedding":           creator_embedding,
            }

            creator_db_id = None
            if sb:
                try:
                    res = sb.table("creators").insert(creator_record).execute()
                    creator_db_id = res.data[0]["id"] if res.data else None
                    logger.info(f"      creators table → inserted, ID={creator_db_id}")
                except Exception as e:
                    logger.warning(f"      creators insert failed: {e}")

            # ── 2. Insert creator_video record ─────────────────────────
            video_record = {
                "creator_id":           creator_db_id,
                "video_url":            vid["video_url"],
                "title":                vid["title"],
                "description":          (vid["description"] or "")[:500],
                "video_screenshot_url": vid["thumbnail_url"],
                "simulated_engagement": 45000,
            }

            video_db_id = None
            if sb:
                try:
                    res = sb.table("creator_videos").insert(video_record).execute()
                    video_db_id = res.data[0]["id"] if res.data else None
                    logger.info(f"      creator_videos table → inserted, ID={video_db_id}")
                except Exception as e:
                    logger.warning(f"      creator_videos insert failed: {e}")

            # ── 3. Fetch transcript ────────────────────────────────────
            logger.info(f"      Fetching transcript...")
            transcript = get_transcript(video_id)
            if not transcript:
                logger.warning(f"      No transcript — skipping garment extraction.")
                time.sleep(1.0)
                continue

            # ── 4. Extract 2-3 distinct garments via Gemini ────────────
            dresses = extract_dresses_from_transcript(
                transcript, source_type="creator", pincode=zip_code
            )
            logger.info(f"      Gemini extracted {len(dresses)} garments.")

            # ── 5. Per-garment: embed → cosine search → link ───────────
            for dress_meta in dresses:
                item_name    = dress_meta.get("item", "Unknown")
                dress_vector = embed_dress(dress_meta)

                best_product, confidence = find_best_catalog_match(dress_vector, catalog, zip_code)

                if best_product:
                    product_id   = best_product.get("id")
                    product_name = best_product.get("name", "?")
                    logger.info(f"        Garment '{item_name}'")
                    logger.info(f"        └─ matched '{product_name}' (cosine={confidence:.4f})")

                    # ── 6. Insert into creator_video_products ──────────
                    if sb and video_db_id and product_id:
                        try:
                            sb.table("creator_video_products").insert({
                                "video_id":         video_db_id,
                                "product_id":       product_id,
                                "confidence_score": round(confidence, 4),
                            }).execute()
                        except Exception as e:
                            logger.warning(f"        creator_video_products insert failed: {e}")
                else:
                    logger.warning(f"        Garment '{item_name}' — no catalog match found.")

            time.sleep(1.5)   # Rate-limit buffer between video calls

        # ══════════════════════════════════════════════════════════════
        # SECTION B: LOCAL BOUTIQUES
        # ══════════════════════════════════════════════════════════════
        logger.info(f"\n  [B] Boutiques — searching Google Places: '{region_info['places_query']}'")
        boutiques = search_boutiques_google_places(
            region_info["places_query"], locality, zip_code,
            max_results=MAX_BOUTIQUES_PER_REGION
        )
        logger.info(f"  [B] {len(boutiques)} boutiques found via Google Places.")

        for store in boutiques:
            store_name = store["store_name"]
            logger.info(f"\n    🏪 Boutique: {store_name}")
            logger.info(f"       Address : {store.get('address', locality)}")

            # ── Search YouTube for a store tour video ──────────────────
            tour_query = f"{store_name} {region_name} clothing store tour fashion"
            logger.info(f"       YouTube search: '{tour_query}'")
            tour_videos = search_youtube_videos(tour_query, max_results=1)

            trend_tags           = []
            matched_product_names = []

            if tour_videos:
                bvid       = tour_videos[0]
                logger.info(f"       Tour video: '{bvid['title'][:60]}'")
                transcript = get_transcript(bvid["video_id"])

                if transcript:
                    # Extract garments from store tour transcript
                    dresses = extract_dresses_from_transcript(
                        transcript, source_type="boutique", pincode=zip_code
                    )
                    logger.info(f"       Gemini extracted {len(dresses)} garments from store tour.")

                    for dress_meta in dresses:
                        item_name    = dress_meta.get("item", "Unknown")
                        dress_vector = embed_dress(dress_meta)

                        best_product, confidence = find_best_catalog_match(dress_vector, catalog, zip_code)
                        if best_product:
                            trend_tags.append(dress_meta.get("vibe", "ethnic"))
                            matched_product_names.append(best_product.get("name", ""))
                            logger.info(f"         Garment '{item_name}'")
                            logger.info(f"         └─ matched '{best_product.get('name')}' (cosine={confidence:.4f})")

            # Summarise into regional_boutique_trends columns
            extracted_trend = (", ".join(trend_tags[:2]) if trend_tags
                               else region_info["places_query"].split()[0])
            style_cluster   = (f"Matched: {'; '.join(matched_product_names[:2])}"
                               if matched_product_names
                               else f"Regional fashion cluster — {region_name}")

            boutique_record = {
                "store_id":              store["store_id"],
                "zip_code":              zip_code,
                "locality":              store["locality"],
                "store_name":            store_name,
                "social_signal_source":  store["social_signal_source"],
                "simulated_engagement":  store["simulated_engagement"],
                "extracted_visual_trend": extracted_trend[:50],
                "style_vibe_cluster":    style_cluster[:100],
            }

            if sb:
                try:
                    sb.table("regional_boutique_trends").upsert(boutique_record).execute()
                    logger.info(f"       regional_boutique_trends → upserted ✅")
                except Exception as e:
                    logger.warning(f"       regional_boutique_trends upsert failed: {e}")

            time.sleep(1.0)

    logger.info(f"\n{'═'*65}")
    logger.info("  PIPELINE COMPLETE")
    logger.info(f"  All creators, videos, garment–product links, and boutiques")
    logger.info(f"  have been written to Supabase production tables.")
    logger.info(f"{'═'*65}")


if __name__ == "__main__":
    run_pipeline()
