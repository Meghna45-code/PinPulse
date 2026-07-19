import os
import sys
import json
import time
import logging
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import numpy as np
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("re_enrich_all_catalog_vision")

load_dotenv("backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found in environment!")
    sys.exit(1)

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_vibe_vector_from_tags(tags: list):
    """Deterministic 512-dimensional vector based on list of tags."""
    vec = np.zeros(512)
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in ["ethnic", "festive", "saree", "lehenga", "traditional", "jainsem", "jymphong", "mundu", "sherwani", "ceremonial", "heavy_silk", "traditional_embroidery"]:
            vec[0:100] += 1.0
        if tag_lower in ["casual", "summer", "linen", "cotton", "breathable", "dailywear"]:
            vec[100:200] += 1.0
        if tag_lower in ["winter", "warm", "heavy-weight", "velvet", "shawl", "jacket", "cardigan", "woolen"]:
            vec[200:300] += 1.0
        if tag_lower in ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party", "trendy"]:
            vec[300:400] += 1.0
            
    vec[400:512] = 0.2
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
        
    return vec.tolist()

def load_image(image_url):
    """Load image either from a URL or local file path."""
    if image_url.startswith("http://") or image_url.startswith("https://"):
        try:
            logger.info(f"Downloading remote image from URL: {image_url}")
            r = requests.get(image_url, timeout=10)
            r.raise_for_status()
            return Image.open(BytesIO(r.content))
        except Exception as e:
            logger.error(f"Failed to download remote image {image_url}: {e}")
            return None
    else:
        filename = os.path.basename(image_url)
        # Try public images directory
        local_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(local_path):
            try:
                return Image.open(local_path)
            except Exception as e:
                logger.error(f"Failed to open local image at {local_path}: {e}")
                
        # Try fallback name check (e.g. if we have various extensions)
        name_only = os.path.splitext(filename)[0]
        for ext in [".webp", ".png", ".jpg", ".jpeg", ".avif"]:
            alt_path = os.path.join(IMAGES_DIR, f"{name_only}{ext}")
            if os.path.exists(alt_path):
                try:
                    return Image.open(alt_path)
                except:
                    pass
        logger.warning(f"Local image not found for path/url: {image_url}")
        return None

def call_gemini_vision(img, keywords):
    """Call Gemini Vision model to identify and describe the apparel product."""
    prompt = f"""
    Analyze the fashion apparel product image. Identify the clothing item, footwear, or accessory shown.
    The original metadata keywords are: "{keywords}".
    
    Return a valid JSON object matching this schema:
    {{
      "name": "A premium, clear, short fashion title for the item (e.g. 'Banarasi Silk Saree', 'Heeled Leather Boot', 'Striped Linen Casual Shirt', 'Embroidered Sherwani Set'). Do not use generic names; ensure it matches the exact style shown. Keep it under 5-6 words.",
      "category": "Must be one of 'ethnic', 'western', 'winter', 'streetwear', 'casual', 'accessories', 'footwear'",
      "material": "The dominant fabric material (e.g., Silk, Cotton, Linen, Wool, Leather, Denim, Velvet, Polyester, Suede, Rayon)",
      "color": "The primary color or 'Multi' if multi-colored",
      "nature": "The style vibe or occasion suitability: must be one of 'casual', 'formal', 'festive'",
      "age_range": "The target demographic: must be one of 'Gen Z', 'Millennial'",
      "description": "A highly detailed, professional, contextual description of the apparel (1-2 sentences), suitable for a premium fashion website. DO NOT include hashtags. Describe EXACTLY what is shown in the image. Ensure the name and description align perfectly with the image."
    }}
    """
    try:
        model = genai.GenerativeModel('models/gemini-flash-lite-latest')
        response = model.generate_content([img, prompt])
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini API call failed: {e}")
        return None

def main():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error(f"Catalog file not found at {LOCAL_CATALOG_FILE}")
        return

    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Allow limiting for test runs
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            logger.info(f"Limiting run to first {limit} products.")
        except ValueError:
            pass

    logger.info(f"Loaded local catalog with {len(catalog)} products.")

    supabase = None
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase.")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")

    # Set up model & run loop
    success_count = 0
    start_time = time.time()

    # Track unique descriptions to prevent duplicates
    generated_descriptions = set()

    for idx, p in enumerate(catalog):
        if limit and success_count >= limit:
            logger.info(f"Reached limit of {limit} products, stopping.")
            break
        pid = p["id"]
        image_url = p.get("image_url", "")
        keywords = p.get("description", p.get("name", ""))
        
        logger.info(f"[{idx+1}/{len(catalog)}] Processing Product ID {pid}...")
        
        img = load_image(image_url)
        if not img:
            logger.warning(f"Skipping Product ID {pid} because image could not be loaded.")
            continue

        llm_data = call_gemini_vision(img, keywords)
        
        if not llm_data:
            logger.error(f"Failed to enrich Product ID {pid} via Gemini Vision.")
            continue

        # Prevent duplicate descriptions by adding a small suffix/variation if description already generated
        desc = llm_data["description"].strip()
        orig_desc = desc
        dup_check = desc.lower()
        dup_counter = 1
        while dup_check in generated_descriptions:
            desc = f"{orig_desc} This premium variant {dup_counter} is styled for unique fashion vibes."
            dup_check = desc.lower()
            dup_counter += 1
        generated_descriptions.add(dup_check)

        # Update product catalog values
        p["name"] = llm_data["name"]
        p["description"] = desc
        p["material"] = llm_data["material"]
        p["color"] = llm_data["color"]
        p["nature"] = llm_data["nature"]
        p["age_range"] = llm_data["age_range"]
        p["category"] = llm_data["category"].lower()

        # Build custom tags
        new_tags = set()
        new_tags.add(p["category"])
        new_tags.add(p["material"].lower())
        new_tags.add(p["color"].lower())
        new_tags.add(p["nature"].lower())
        new_tags.add(p["age_range"].lower())
        
        # Add name keywords as tags for search matching
        for word in p["name"].lower().split():
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 2:
                new_tags.add(clean_word)
                
        p["tags"] = list(new_tags)

        # Re-generate embedding
        p["embedding"] = get_vibe_vector_from_tags(p["tags"])

        # Sync to local catalog incrementally
        with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)

        # Sync to Supabase
        if supabase:
            try:
                payload = {
                    "id": pid,
                    "name": p["name"],
                    "description": p["description"],
                    "image_url": p["image_url"],
                    "product_url": p["product_url"],
                    "tags": p["tags"],
                    "zip_codes": p.get("zip_codes", []),
                    "embedding": p["embedding"],
                    "price": p.get("price", 1099),
                    "inventory": p.get("inventory", 15),
                    "material": p["material"],
                    "color": p["color"],
                    "nature": p["nature"],
                    "age_range": p["age_range"],
                    "category": p["category"]
                }
                supabase.table("products").upsert(payload).execute()
                logger.info(f"  Successfully synced Product ID {pid} to Supabase: {p['name']}")
            except Exception as e:
                logger.error(f"  Failed to sync Product ID {pid} to Supabase: {e}")

        success_count += 1
        
        # Rate limit control: 15 RPM max is 1 call every 4s
        time.sleep(4.1)

    # Save to frontend catalog fallback js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w", encoding="utf-8") as f:
                f.write(js_content)
            logger.info("Successfully updated frontend fallback catalog file.")
        except Exception as e:
            logger.error(f"Failed to update frontend fallback: {e}")

    duration = time.time() - start_time
    logger.info(f"Finished re-enriching all {success_count} products. Duration: {duration:.2f} seconds.")

if __name__ == "__main__":
    main()
