"""
PinPulse Mock Database Seeder  (HACKATHON — Local JSON Cache)
=============================================================
This script is triggered when a team member uploads an Excel file
(pinpulse_youtube_seed.xlsx) containing Video IDs for local creators
and boutiques.

Architecture per row in the Excel sheet:
  1. YouTubeTranscriptApi   →  full transcript text
  2. Gemini LLM             →  extract 2-3 distinct garments from the transcript
  3. get_vibe_vector()      →  generate a SEPARATE 512-dim vector per garment
  4. Cosine similarity      →  match each garment vector against the Myntra catalog
  5. JSON export            →  append all garment+match records to pinpulse_mock_db.json

Expected Excel columns:
  video_id   — 11-character YouTube video ID
  pincode    — ZIP code (800008 / 682001 / 752001)
  type       — 'creator' or 'boutique'
  store_name — (optional) store name for boutique entries

Output:
  backend/pinpulse_mock_db.json
"""

import os
import sys
import json
import logging
import numpy as np
import pandas as pd
from dotenv import load_dotenv

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Import the EXACT same embedding model used for the Myntra catalog
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

MAX_DRESSES_PER_VIDEO = 3  # Gemini will extract up to this many garments per video


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
    """Cosine similarity search to find the best matching catalog product for a dress."""
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
    Generate a 512-dim vector for a single garment.
    Uses the same get_vibe_vector() as the Myntra catalog
    to maintain mathematical parity in cosine space.
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
        logger.error(f"  Failed to fetch transcript for {video_id}: {e}")
        return None


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GEMINI GARMENT EXTRACTION                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def extract_dresses_from_transcript(transcript_text, is_creator=True, pincode="800008"):
    """
    Sends the transcript to Gemini and extracts 2-3 distinct garment descriptions.
    Returns a list of dicts.
    """
    if not GEMINI_API_KEY or not transcript_text:
        return []

    if is_creator:
        prompt = f"""
You are an AI fashion extractor. Read this video transcript from a local lifestyle creator.
Identify exactly 2 or 3 DISTINCT clothing items or outfits being shown or discussed.
For EACH item, return one JSON object.

Return ONLY a valid JSON array — no markdown, no extra text:
[
  {{"item": "maroon silk Banarasi saree", "fabric": "silk", "color": "maroon", "vibe": "festive ethnic", "occasion": "wedding"}},
  {{"item": "yellow cotton kurti", "fabric": "cotton", "color": "yellow", "vibe": "casual ethnic", "occasion": "college"}}
]

Transcript (pincode {pincode}):
{transcript_text[:3000]}
"""
    else:
        prompt = f"""
You are an AI retail inventory extractor. Read this transcript from a local boutique or store tour.
Identify exactly 2 or 3 DISTINCT clothing items on display.
For EACH item, return one JSON object.

Return ONLY a valid JSON array — no markdown, no extra text:
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
        logger.error(f"  Gemini garment extraction failed: {e}")
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

    all_records = []
    dress_counter = 0

    for _, row in df.iterrows():
        video_id   = str(row.get("video_id", "")).strip()
        pincode    = str(row.get("pincode", "800008")).strip()
        feed_type  = str(row.get("type", "creator")).strip().lower()
        store_name = str(row.get("store_name", "Unknown")).strip()

        if not video_id or video_id == "nan":
            continue

        logger.info(f"\n  Processing ({feed_type}) Video ID: {video_id}  [{pincode}]")

        # ── 1. Fetch transcript ─────────────────────────────────────
        transcript = get_transcript(video_id)
        if not transcript:
            continue

        # ── 2. Extract 2-3 garments via Gemini ─────────────────────
        is_creator = (feed_type == "creator")
        dresses = extract_dresses_from_transcript(
            transcript, is_creator=is_creator, pincode=pincode
        )
        logger.info(f"  Gemini extracted {len(dresses)} garments.")

        # ── 3. Per-garment: embed → cosine match → build record ─────
        for dress_meta in dresses:
            item_name    = dress_meta.get("item", "Unknown")
            dress_vector = embed_dress(dress_meta)

            best_product, confidence = find_best_catalog_match(dress_vector, catalog, pincode)

            matched_product_id   = best_product.get("id")    if best_product else None
            matched_product_name = best_product.get("name")  if best_product else None

            logger.info(f"    Garment: '{item_name}'")
            if best_product:
                logger.info(f"    └─ matched '{matched_product_name}' (cosine={confidence:.4f})")
            else:
                logger.info(f"    └─ no catalog match found.")

            # ── 4. Build unified record ─────────────────────────────
            dress_counter += 1
            record = {
                "id":                   f"{pincode}_{feed_type}_{video_id}_{dress_counter}",
                "type":                 feed_type,
                "pincode":              pincode,
                "video_id":             video_id,
                "metadata":             dress_meta,
                "vector":               dress_vector,
                "matched_product_id":   matched_product_id,
                "matched_product_name": matched_product_name,
                "match_confidence":     round(confidence, 4) if best_product else 0.0,
            }

            if not is_creator:
                record["store_name"] = dress_meta.get("store_name", store_name)

            all_records.append(record)

    # ── Write output ────────────────────────────────────────────────────────
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=4)

    logger.info(f"\n{'='*60}")
    logger.info(f"  Seeding complete!")
    logger.info(f"  {len(all_records)} garment records exported to {OUTPUT_FILE}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    excel_input = sys.argv[1] if len(sys.argv) > 1 else "pinpulse_youtube_seed.xlsx"
    process_seeding_from_excel(excel_input)
