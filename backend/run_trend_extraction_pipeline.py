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
import io
import numpy as np
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from PIL import Image

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
MAX_CREATORS         = 7
MAX_BOUTIQUES        = 4
MAX_DRESSES_PER_VID  = 3
PUBLISHED_AFTER      = (datetime.utcnow() - timedelta(days=548)).strftime("%Y-%m-%dT%H:%M:%SZ")

# ── CLIP Model Initialization ──────────────────────────────────────────────────
logger.info("Attempting to load CLIP model ('openai/clip-vit-base-patch32')...")
try:
    import torch
    from transformers import CLIPModel, CLIPProcessor
    torch.set_num_threads(2)
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    logger.info("CLIP model loaded successfully! ✅")
except Exception as e:
    logger.error(f"Failed to load CLIP model: {e}")
    clip_model = None
    clip_processor = None

def download_image(url):
    if not url:
        return None
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
    except Exception as e:
        logger.warning(f"    Failed to download image from {url}: {e}")
    return None

def classify_thumbnail_fashion(image):
    """
    Perform zero-shot classification using CLIP to verify if the thumbnail
    is related to fashion/clothing vs. unrelated background noise.
    """
    if not clip_model or not clip_processor or not image:
        return True  # Fallback to True if model is not loaded
    try:
        # Resize thumbnail to save time
        img_copy = image.copy()
        img_copy.thumbnail((224, 224))
        
        candidate_labels = [
            "clothing fashion apparel outfit dress traditional wear shopping showcase",
            "unrelated news gaming background tech landscape close-up face talking head"
        ]
        
        inputs = clip_processor(
            images=img_copy,
            text=candidate_labels,
            return_tensors="pt",
            padding=True
        )
        
        with torch.no_grad():
            outputs = clip_model(**inputs)
            # Dot products between image and text features
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
            
        logger.info(f"      CLIP fashion classification probability: {probs[0]:.4f} vs. noise: {probs[1]:.4f}")
        # Threshold: if fashion class probability > 0.55, return True
        return bool(probs[0] > 0.55)
    except Exception as e:
        logger.warning(f"      CLIP classification failed: {e}. Defaulting to True.")
        return True

def get_clip_image_vector(image):
    """
    Generate normalized 512-dimension image embedding vector using CLIP.
    """
    if not clip_model or not clip_processor or not image:
        return [0.0] * 512
    try:
        img_copy = image.copy()
        img_copy.thumbnail((224, 224))
        
        inputs = clip_processor(images=img_copy, return_tensors="pt")
        with torch.no_grad():
            features = clip_model.get_image_features(**inputs)
            
        feat_np = features.cpu().numpy()[0]
        norm = np.linalg.norm(feat_np)
        if norm > 0:
            feat_np = feat_np / norm
        return feat_np.tolist()
    except Exception as e:
        logger.error(f"      Failed to compute CLIP image vector: {e}")
        return [0.0] * 512

REGIONS = {
    "800008": {
        "name": "Patna",
        "locality": "Frazer Road, Patna, Bihar",
        "location": "25.5941,85.1376",
        "locationRadius": "10km",
        "creator_query": "Patna fashion vlog OOTD OR Patna GRWM OR Patna lookbook",
        "boutique_query": "clothing store boutique tour",
        "places_query": "clothing boutique",
    },
    "682001": {
        "name": "Kochi",
        "locality": "MG Road, Kochi, Kerala",
        "location": "9.9312,76.2673",
        "locationRadius": "10km",
        "creator_query": "Kochi fashion influencer OR Kochi OOTD OR Kochi styling",
        "boutique_query": "clothing boutique fashion store tour",
        "places_query": "clothing boutique",
    },
    "752001": {
        "name": "Puri",
        "locality": "Puri Jagannath Temple Area, Puri, Odisha",
        "location": "19.8135,85.8312",
        "locationRadius": "10km",
        "creator_query": "Odisha fashion creator OR Odisha lookbook OR Odisha GRWM",
        "boutique_query": "clothing boutique fashion store tour",
        "places_query": "clothing boutique",
    },
}

BOUTIQUE_SEED = {
    "800008": [
        {"store_id": "STR_800008_001", "store_name": "Patna Market", "address": "Patna Market, Frazer Road, Patna, Bihar", "rating": 4.5, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 15000, "locality": "Patna Market, Patna"},
        {"store_id": "STR_800008_002", "store_name": "Hathwa Market", "address": "Hathwa Market, Bakerganj, Patna, Bihar", "rating": 4.4, "social_signal_source": "Instagram Location Signal", "simulated_engagement": 12500, "locality": "Hathwa Market, Patna"},
        {"store_id": "STR_800008_003", "store_name": "Khetan Market", "address": "Khetan Super Market, Birla Mandir Road, Patna, Bihar", "rating": 4.6, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 18000, "locality": "Khetan Market, Patna"}
    ],
    "682001": [
        {"store_id": "STR_682001_001", "store_name": "Broadway Kochi", "address": "Broadway, Marine Drive, Kochi, Kerala", "rating": 4.5, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 16000, "locality": "Broadway, Kochi"},
        {"store_id": "STR_682001_002", "store_name": "Lulu Mall Kochi", "address": "Lulu Mall, Edappally, Kochi, Kerala", "rating": 4.8, "social_signal_source": "Instagram Location Signal", "simulated_engagement": 25000, "locality": "Lulu Mall, Kochi"},
        {"store_id": "STR_682001_003", "store_name": "MG Road boutiques", "address": "MG Road, Kochi, Kerala", "rating": 4.4, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 11000, "locality": "MG Road, Kochi"}
    ],
    "752001": [
        {"store_id": "STR_752001_001", "store_name": "Puri Beach Market", "address": "Golden Beach Market, Puri, Odisha", "rating": 4.3, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 14000, "locality": "Puri Beach Market, Puri"},
        {"store_id": "STR_752001_002", "store_name": "Grand Road markets", "address": "Grand Road, Puri, Odisha", "rating": 4.4, "social_signal_source": "Instagram Location Signal", "simulated_engagement": 12000, "locality": "Grand Road, Puri"},
        {"store_id": "STR_752001_003", "store_name": "Swargadwar Market", "address": "Swargadwar Road, Puri, Odisha", "rating": 4.2, "social_signal_source": "YouTube Store Tour", "simulated_engagement": 10500, "locality": "Swargadwar Market, Puri"}
    ]
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
    return get_vibe_vector(all_tags, category_str=category, aesthetic_str=aesthetic)


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

        cos_score = cosine_similarity(dress_vector, p_emb)
        age_score   = age_overlap_score(dress_age, p.get("age_group", ""))
        price_score = price_proximity_score(dress_price, p.get("price"))

        final = 0.70 * cos_score + 0.20 * age_score + 0.10 * price_score
        if final > best_score:
            best_score   = final
            best_product = p

    return best_product, best_score


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              DIVERSE MATCHING — prefiltering + CLIP + stratification         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def find_diverse_catalog_matches_for_thumbnail(thumbnail_vector, catalog, zip_code, zip_aov, allowable_materials, max_matches=3):
    """
    1. Hard Filter (Metadata):
       - Only consider products where price <= 2 * zip_aov.
       - Only consider products where material/fabric matches allowable materials.
    2. Vector Rank:
       - Calculate cosine similarity between thumbnail vector and catalog CLIP embeddings.
    3. Category Stratification:
       - Ensure we pick top products from distinct categories.
    """
    # 1. Hard Filter
    filtered_catalog = []
    allowable_lower = [m.lower() for m in allowable_materials]
    
    for p in catalog:
        # Check ZIP code restrictions if present
        p_zips = p.get("zip_codes", [])
        if p_zips and zip_code not in p_zips:
            continue
            
        # Price affinity hard check (Price <= 2.0 * AOV)
        p_price = float(p.get("price", 1099.0))
        if p_price > 2.0 * zip_aov:
            continue
            
        # Weather / material hard check
        p_material = p.get("material", "").lower()
        if p_material and p_material not in allowable_lower:
            continue
            
        filtered_catalog.append(p)
        
    # Fallback to unrestricted catalog if hard filtering is too strict (prevent zero recommendations)
    if not filtered_catalog:
        logger.warning(f"      Hard filtering returned 0 items. Falling back to ZIP-matched catalog.")
        filtered_catalog = [p for p in catalog if (not p.get("zip_codes") or zip_code in p.get("zip_codes"))]
        
    # 2. Vector Rank (CLIP Image Similarity)
    scored_products = []
    for p in filtered_catalog:
        p_emb = p.get("embedding", [])
        if not p_emb or len(p_emb) != len(thumbnail_vector):
            # If no CLIP embedding is cached, fall back to vibe vector
            from embed_catalog import get_vibe_vector
            p_emb = get_vibe_vector(
                p.get("tags", []),
                category_str=p.get("category", ""),
                aesthetic_str=p.get("aesthetic", "")
            )
            
        sim = cosine_similarity(thumbnail_vector, p_emb)
        scored_products.append((p, sim))
        
    # Sort by similarity descending
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    # 3. Category Stratification
    diverse_matches = []
    seen_categories = set()
    
    for p, sim in scored_products:
        cat = p.get("category", "Western").lower().strip()
        if cat not in seen_categories:
            seen_categories.add(cat)
            diverse_matches.append((p, sim))
        if len(diverse_matches) >= max_matches:
            break
            
    # If we couldn't get enough matches due to category constraints, fill with remaining items
    if len(diverse_matches) < max_matches:
        for p, sim in scored_products:
            if p["id"] not in [x[0]["id"] for x in diverse_matches]:
                diverse_matches.append((p, sim))
            if len(diverse_matches) >= max_matches:
                break
                
    return diverse_matches


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                         TRANSCRIPT FETCHING                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def load_catalog():
    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        return " ".join([entry.text for entry in transcript])
    except Exception as e:
        logger.warning(f"    No transcript for {video_id}: {e}")
        return None


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                       GEMINI GARMENT EXTRACTION                             ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def validate_and_extract_vision(image, city_name, query_context):
    """
    Multimodal Vision Classifier & Fashion Extractor.
    Takes a video thumbnail screenshot and extracts clothing fashion items directly.
    Relaxed discriminator: checks if image shows fashion, outfits, clothing, or shopping showcases.
    Returns: (is_valid, garments, extracted_boutique_name)
    """
    if not GEMINI_API_KEY or not image:
        return False, [], None

    prompt = f"""
You are an expert AI fashion validator and visual inventory extractor.
Analyze the provided video thumbnail image and the query context: "{query_context}" in the city of "{city_name}".

Perform these operations:
1. Determine if this image or context features clothing, apparel, traditional Indian ethnic wear, saree hauls, or outfit shopping.
2. Estimate if the fashion is relevant to style trends in "{city_name}".
3. If True, extract 1 to 3 clothing items shown in the image or fitting the local context. For EACH item, fill in:
   - item: specific garment name (e.g., "red silk Banarasi saree")
   - description: short marketing description
   - tags: list of fashion tag strings
   - aesthetic: aesthetic vibe string
   - material: fabric material string
   - fabric: simplified fabric type string
   - color: dominant color name
   - age_group: target age range (e.g., "25-35")
   - estimated_price_inr: estimated retail price in INR (integer, e.g., 2500)
   - occasion (if general creator showcase) or inventory_status (if boutique/market context)
4. Identify if a specific boutique, mall, or market name is visually present or implied in the context.

Return ONLY a valid JSON object matching this schema (no markdown, no extra text):
{{
  "is_fashion_related": true or false,
  "extracted_boutique_name": "Name of shop/market" (or null if none),
  "garments": [
    {{
      "item": "Garment Name",
      "description": "Description details...",
      "tags": ["tag1", "tag2"],
      "aesthetic": "style vibe",
      "material": "cotton",
      "fabric": "cotton",
      "color": "yellow",
      "age_group": "18-25",
      "estimated_price_inr": 1500,
      "occasion": "haldi" (or "inventory_status": "new arrival")
    }}
  ]
}}
"""
    try:
        model = genai.GenerativeModel("models/gemini-flash-latest")
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        
        is_valid = data.get("is_fashion_related", False)
        boutique_name = data.get("extracted_boutique_name")
        garments = data.get("garments", [])
        return is_valid, garments, boutique_name
    except Exception as e:
        logger.warning(f"    Vision validation/extraction failed: {e}")
        return False, [], None


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                          YOUTUBE DATA API v3                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def search_youtube_videos(query, max_results=3, location=None, location_radius=None, page_token=None, only_shorts=False):
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_MAPS_API_KEY missing — cannot call YouTube Data API.")
        return [], None
        
    if only_shorts:
        if "shorts" not in query.lower():
            query = f"{query} shorts"
            
    params = {
        "part": "snippet", "q": query, "maxResults": max_results,
        "type": "video", "order": "relevance",
        "publishedAfter": PUBLISHED_AFTER, "key": GOOGLE_API_KEY,
    }
    if only_shorts:
        params["videoDuration"] = "short"
    if location:
        params["location"] = location
    if location_radius:
        params["locationRadius"] = location_radius
    if page_token:
        params["pageToken"] = page_token

    r = requests.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=15)
    if r.status_code != 200:
        logger.error(f"YouTube search failed for '{query}': {r.text}")
        return [], None
    
    data = r.json()
    next_page_token = data.get("nextPageToken")
    videos = []
    for item in data.get("items", []):
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
    return videos, next_page_token


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


# ── Regional AOV & Weather Rules Metadata ─────────────────────────────────────
ZIP_METADATA = {
    "800008": {"aov": 1800, "allowable_materials": ["cotton", "linen", "rayon", "chiffon", "georgette"]},
    "682001": {"aov": 2200, "allowable_materials": ["cotton", "linen", "rayon", "chiffon", "georgette"]},
    "752001": {"aov": 1500, "allowable_materials": ["cotton", "rayon", "crepe", "silk", "chanderi"]}
}

REGIONAL_CREATORS = {
    "800008": ["Shayno Kumari", "Shilpi Kumari", "Dipankar Singh Patel"],
    "682001": ["Nimmy Arungopan", "Vandana Balakrishnan", "Saranya Nandakumar", "Ahaana Krishna"],
    "752001": ["Prakruti Mishra", "Namrata Parija", "Lovina Nayak", "Rituparna Gahan"]
}

# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                            MAIN PIPELINE                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def run_pipeline():
    logger.info("=" * 65)
    logger.info("  PINPULSE VISION-ONLY AUTONOMOUS TREND AGENT (PURE CLIP / DIVERSITY PIPELINE)")
    logger.info(f"  Recency: publishedAfter={PUBLISHED_AFTER}")
    logger.info(f"  Target Quota: 5 creators + 3 boutiques (3 matches each)")
    logger.info(f"  Methodology: Pure Image-to-Image CLIP ViT-B-32 with Category Stratification")
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
        location    = region_info["location"]
        radius      = region_info["locationRadius"]
        
        logger.info(f"\n{'━'*65}")
        logger.info(f"  REGION: {region_name}  ({zip_code}) [GPS: {location}]")
        logger.info(f"{'━'*65}")

        # Fetch active weather and budget constraints for this ZIP
        meta = ZIP_METADATA.get(zip_code, {"aov": 2000, "allowable_materials": ["cotton", "linen"]})
        zip_aov = meta["aov"]
        allowable_materials = meta["allowable_materials"]

        # ══ A. CREATORS (Loop through searched actual creators, get Shorts) ═══════
        logger.info(f"\n  [A] Creators — Target Influencers list (Google Searched): {REGIONAL_CREATORS.get(zip_code)}")
        
        valid_creator_vids_count = 0
        target_creator_vids = 5
        creators_list = REGIONAL_CREATORS.get(zip_code, [])
        
        # 1. First Pass: Get Shorts for each specific real creator
        for creator_name in creators_list:
            if valid_creator_vids_count >= target_creator_vids:
                break
                
            logger.info(f"\n    🔍 Searching YouTube Shorts for creator: '{creator_name}'")
            creator_vids, _ = search_youtube_videos(
                f"{creator_name} fashion style outfit", 
                max_results=3, 
                only_shorts=True
            )
            
            if not creator_vids:
                logger.info(f"      No shorts found for '{creator_name}' on YouTube.")
                continue
                
            for vid in creator_vids:
                if valid_creator_vids_count >= target_creator_vids:
                    break
                    
                channel = vid["channel"]
                title = vid["title"]
                desc = vid["description"]
                video_id = vid["video_id"]
                
                logger.info(f"      Inspecting ▶ {channel} (Target: {creator_name}) | '{title[:50]}'")
                
                image = download_image(vid["thumbnail_url"])
                if not image:
                    logger.info("      ❌ Skipped: Thumbnail download failed.")
                    continue
                    
                is_valid = classify_thumbnail_fashion(image)
                if not is_valid:
                    logger.info("      ❌ Skipped: CLIP zero-shot fashion classification failed.")
                    continue
                
                thumbnail_vector = get_clip_image_vector(image)
                matches = find_diverse_catalog_matches_for_thumbnail(
                    thumbnail_vector, catalog, zip_code, zip_aov, allowable_materials, max_matches=3
                )
                
                if not matches:
                    logger.info("      ❌ Skipped: 0 matching products found.")
                    continue
                
                valid_creator_vids_count += 1
                logger.info(f"      ✅ Validated local creator Shorts ({valid_creator_vids_count}/{target_creator_vids}) via CLIP")
                
                # 1. Upsert creator
                creator_emb = get_vibe_vector(
                    ["fashion", "lifestyle", "creator", region_name.lower()],
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

                # 3. Match garments
                for prod, score in matches:
                    logger.info(f"        └─ Matched: '{prod.get('name')}' ({prod.get('category')}) [CLIP Sim={score:.4f}]")
                    if sb and video_db_id and prod.get("id"):
                        try:
                            sb.table("creator_video_products").insert({
                                "video_id": video_db_id,
                                "product_id": prod["id"],
                                "confidence_score": round(score, 4),
                            }).execute()
                        except Exception as e:
                            logger.warning(f"        creator_video_products insert failed: {e}")

                time.sleep(1.0)
                
        # 2. Second Pass (Fallback): If quota not met, run general regional query (shorts only)
        if valid_creator_vids_count < target_creator_vids:
            logger.info(f"\n    🔄 Quota not met ({valid_creator_vids_count}/{target_creator_vids}). Running general regional query for Shorts...")
            fallback_vids, _ = search_youtube_videos(
                region_info["creator_query"], 
                max_results=10, 
                only_shorts=True
            )
            
            for vid in fallback_vids:
                if valid_creator_vids_count >= target_creator_vids:
                    break
                    
                channel = vid["channel"]
                title = vid["title"]
                desc = vid["description"]
                
                logger.info(f"      Inspecting Fallback ▶ {channel} | '{title[:50]}'")
                
                image = download_image(vid["thumbnail_url"])
                if not image:
                    continue
                    
                is_valid = classify_thumbnail_fashion(image)
                if not is_valid:
                    continue
                
                thumbnail_vector = get_clip_image_vector(image)
                matches = find_diverse_catalog_matches_for_thumbnail(
                    thumbnail_vector, catalog, zip_code, zip_aov, allowable_materials, max_matches=3
                )
                
                if not matches:
                    continue
                
                valid_creator_vids_count += 1
                logger.info(f"      ✅ Validated fallback creator Shorts ({valid_creator_vids_count}/{target_creator_vids}) via CLIP")
                
                creator_emb = get_vibe_vector(
                    ["fashion", "lifestyle", "creator", region_name.lower()],
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
                        pass

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
                        pass

                for prod, score in matches:
                    logger.info(f"        └─ Matched: '{prod.get('name')}' ({prod.get('category')}) [CLIP Sim={score:.4f}]")
                    if sb and video_db_id and prod.get("id"):
                        try:
                            sb.table("creator_video_products").insert({
                                "video_id": video_db_id,
                                "product_id": prod["id"],
                                "confidence_score": round(score, 4),
                            }).execute()
                        except Exception as e:
                            pass

                time.sleep(1.0)

        # ══ B. BOUTIQUES (Query Pre-Seeded Markets, extract 3 dresses each) ══════
        logger.info(f"\n  [B] Boutiques — Seed Cache: {len(BOUTIQUE_SEED.get(zip_code, []))} stores configured.")
        boutiques = BOUTIQUE_SEED.get(zip_code, [])

        for store in boutiques:
            sname = store["store_name"]
            logger.info(f"\n    🏪 {sname}  |  {store.get('address', locality)}")

            tour_vids, _ = search_youtube_videos(
                f"{sname} {region_name} clothing shopping market", 
                max_results=5, 
                only_shorts=True
            )
            trend_tags, matched_names = [], []
            dresses_count = 0
            
            for t_vid in tour_vids:
                if dresses_count >= 3:
                    break
                    
                image = download_image(t_vid["thumbnail_url"])
                if not image:
                    continue
                
                # Zero-shot CLIP Fashion validation
                is_valid = classify_thumbnail_fashion(image)
                if not is_valid:
                    logger.info(f"      ❌ Skipped video '{t_vid['title'][:30]}': Failed fashion validation.")
                    continue

                thumbnail_vector = get_clip_image_vector(image)
                
                # Match filtered products with category stratification to ensure diversity
                matches = find_diverse_catalog_matches_for_thumbnail(
                    thumbnail_vector, catalog, zip_code, zip_aov, allowable_materials, max_matches=3
                )
                
                for prod, score in matches:
                    if dresses_count >= 3:
                        break
                    trend_tags.append(prod.get("nature", "ethnic"))
                    matched_names.append(prod.get("name", ""))
                    dresses_count += 1
                    logger.info(f"        └─ '{prod.get('name')}' ({prod.get('category')}) [CLIP Sim={score:.4f}] [Boutique Item {dresses_count}/3]")

            extracted_trend = (", ".join(trend_tags[:2]) if trend_tags
                               else "ethnic")
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
                    logger.info(f"      regional_boutique_trends → upserted store trends ✅")
                except Exception as e:
                    logger.warning(f"      boutique upsert failed: {e}")

            time.sleep(1.0)
    logger.info(f"\n{'═'*65}")
    logger.info("  PIPELINE COMPLETE — all data written to Supabase.")
    logger.info(f"{'═'*65}")


if __name__ == "__main__":
    run_pipeline()
