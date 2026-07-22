import os
import json
import time
import logging
import random
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from dotenv import load_dotenv
from pinscrape import Pinterest

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pinterest_generator")

load_dotenv(dotenv_path="backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))
CHECKPOINT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "large_catalog_checkpoint.json"))

# Import get_vibe_vector from embed_catalog to keep parity
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from embed_catalog import get_vibe_vector
except ImportError:
    def get_vibe_vector(tags, category_str="casual", aesthetic_str="casual"):
        np.random.seed(hash(" ".join(tags)) % (2**32))
        vec = np.random.randn(512)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

# Define the 10 Vibes
VIBES = [
    "Heritage Traditionalist",
    "Festive Glam",
    "Indie Fusion (Desi Boho)",
    "Minimalist Essentials",
    "High-Street Rebel",
    "Coastal Tropical",
    "Winter Academia",
    "Classic Smart Casual",
    "Bohemian Artsy",
    "Retro Vintage"
]

# Define local events and festivals
FESTIVALS = [
    "Durga Puja", "Diwali", "Chhath Puja", "Saraswati Puja", "Makar Sankranti",
    "Vishu", "Onam", "Holi", "Eid-ul-Fitr", "Wedding Ceremony", "College Farewell",
    "Graduation Ceremony", "Independence Day", "Biennale Art Festival"
]

def get_existing_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_checkpoint(data):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def call_gemini_vision_analysis(img_bytes, query_context):
    """Send real Pinterest image bytes to Gemini for fashion metadata classification."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY missing - cannot run visual analysis.")
        return None
    
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Load image from bytes
    try:
        img = Image.open(BytesIO(img_bytes))
    except Exception as e:
        logger.error(f"Failed to parse image bytes: {e}")
        return None

    model = genai.GenerativeModel("models/gemini-flash-latest")
    
    prompt = f"""
You are an expert AI fashion cataloguer. 
Analyze the provided real clothing dress image from Pinterest in the context of: "{query_context}".

Perform these operations:
1. Confirm if this image contains a garment, outfit, dress, or wearable fashion item. If not, return {{"is_fashion": false}}.
2. Extract the fashion details to form a standard catalog product record:
   - name: Beautiful unique product name (e.g., "Vintage Emerald Velvet Maxi Dress")
   - description: A highly detailed 2-sentence catalog description of the style, cut, and vibe.
   - category: Either "ethnic", "casual", "streetwear", "winter", "formal", "sports", or "accessory".
   - tags: A list of 6 to 8 descriptive fashion keywords (e.g. ["velvet", "green", "vintage", "maxi", "formal", "long-sleeve"]). Do NOT include product_url, image_url, or stock_level in the tags.
   - material: The dominant fabric material (e.g., "silk", "cotton", "velvet", "linen", "denim").
   - color: Dominant color.
   - age_group: Target age category, either "gen-z" or "millennial".
   - price: Estimated realistic price in INR (integer, e.g., 2499).

Strictly return ONLY a valid JSON object matching this schema (no markdown, no backticks, no extra text):
{{
  "is_fashion": true,
  "name": "Product Name",
  "description": "Product description...",
  "category": "casual",
  "tags": ["tag1", "tag2"],
  "material": "fabric",
  "color": "color",
  "age_group": "gen-z",
  "price": 1999
}}
"""
    try:
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        if not data.get("is_fashion", True):
            return None
        return data
    except Exception as e:
        logger.error(f"Gemini vision call failed: {e}")
        return None

def main():
    if not GEMINI_API_KEY:
        logger.error("No GEMINI_API_KEY found. Exiting.")
        return
        
    logger.info("Initializing Real Pinterest Image Catalog Ingestion...")
    
    # 1. Load checkpoint
    generated_items = get_existing_checkpoint()
    logger.info(f"Loaded {len(generated_items)} items from checkpoint.")
    
    target_count = 3100
    
    # Create the Pinterest scraper instance
    p = Pinterest(sleep_time=1)
    
    # Track existing processed URLs to prevent duplicates
    processed_urls = {item["image_url"] for item in generated_items if "image_url" in item}
    
    # Track iteration combinations
    random.seed(42)
    combinations = []
    for vibe in VIBES:
        for festival in FESTIVALS:
            combinations.append((vibe, festival))
            
    random.shuffle(combinations)
    
    comb_idx = 0
    while len(generated_items) < target_count:
        if comb_idx >= len(combinations):
            comb_idx = 0
            random.shuffle(combinations)
            
        vibe, festival = combinations[comb_idx]
        comb_idx += 1
        
        # Search query for Pinterest
        keyword = f"{vibe} {festival} outfit fashion style"
        logger.info(f"Searching Pinterest for: '{keyword}' (Progress: {len(generated_items)}/{target_count})")
        
        try:
            # pinscrape returns a list of HttpUrl objects
            urls_raw = p.search(keyword, 10)
            if not urls_raw:
                logger.warning(f"No pins found for query: '{keyword}'")
                time.sleep(2)
                continue
        except Exception as e:
            logger.error(f"Pinterest search failed: {e}")
            time.sleep(5)
            continue
            
        # Process returned URLs
        for url_obj in urls_raw:
            if len(generated_items) >= target_count:
                break
                
            # Convert HttpUrl to string
            img_url = str(url_obj)
            if img_url in processed_urls:
                continue
                
            processed_urls.add(img_url)
            logger.info(f"  Downloading Pin image: {img_url}")
            
            # Download image bytes
            try:
                img_res = requests.get(img_url, timeout=10)
                if img_res.status_code != 200:
                    continue
                img_bytes = img_res.content
            except Exception as e:
                logger.warning(f"  Failed to download image {img_url}: {e}")
                continue
                
            # Call Gemini Vision to analyze the actual image
            logger.info("  Analyzing image details with Gemini Vision...")
            details = call_gemini_vision_analysis(img_bytes, f"Vibe: {vibe}, Occasion: {festival}")
            
            if not details:
                logger.info("  ❌ Rejected: Not fashion or analysis failed.")
                continue
                
            # Parse and create product entry
            p_id = len(generated_items) + 1000 # Starting IDs from 1000 to prevent collisions
            p_tags = details.get("tags", [])
            
            # Generate 512-dimension vector embedding based on tags
            emb = get_vibe_vector(
                p_tags, 
                category_str=details.get("category", "casual"), 
                aesthetic_str=vibe
            )
            
            product_entry = {
                "id": p_id,
                "name": details.get("name"),
                "description": details.get("description"),
                "category": details.get("category", "casual"),
                "tags": p_tags,
                "material": details.get("material"),
                "color": details.get("color"),
                "nature": vibe,
                "price": details.get("price", 1999),
                "is_evergreen": (p_id % 15 == 0),
                "baseline_sales": (p_id * 3) % 20 + 5,
                "current_sales": ((p_id * 3) % 20 + 5) + (p_id % 5),
                "age_group": details.get("age_group", "millennial"),
                "embedding": emb,
                "image_url": img_url,
                "product_url": "", # Explicitly omit checkout link
                "zip_codes": [] # Available globally
            }
            
            generated_items.append(product_entry)
            logger.info(f"  ✅ Added real Pin dress: '{product_entry['name']}' (Total: {len(generated_items)})")
            
            save_checkpoint(generated_items)
            
            # Polite delay to match Gemini free rate limit (15 requests/min = 4s sleep)
            time.sleep(4)
            
        # Delay between search query combinations
        time.sleep(2)
        
    # Once complete, rewrite the main catalog and sync to Supabase!
    logger.info(f"🎉 Target reached! Total real Pinterest items: {len(generated_items)}")
    
    # Load original catalog items
    with open(LOCAL_CATALOG_FILE, "r") as f:
        original_catalog = json.load(f)
        
    # Strip product_url from original catalog items too!
    for p in original_catalog:
        p["product_url"] = ""
        if "stock_level" in p:
            del p["stock_level"]
            
    # Combine original and generated
    final_catalog = original_catalog + generated_items
    
    # Save locally
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(final_catalog, f, indent=4)
    logger.info(f"Saved total {len(final_catalog)} products to local_catalog.json")
    
    # Save fallback catalog js for frontend
    FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "catalog_fallback.js"))
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(final_catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info("Rewrote frontend catalog_fallback.js")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # Upload to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            
            logger.info("Connected to Supabase. Clearing 'products' table...")
            supabase.table("products").delete().neq("id", 0).execute()
            logger.info("Cleared 'products' table in Supabase.")
            
            logger.info("Uploading combined catalog to Supabase in chunks...")
            DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding"}
            db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in final_catalog]
            
            chunk_size = 100
            for i in range(0, len(db_catalog), chunk_size):
                chunk = db_catalog[i:i+chunk_size]
                supabase.table("products").insert(chunk).execute()
                logger.info(f"Uploaded chunk {i//chunk_size + 1}/{(len(db_catalog)-1)//chunk_size + 1}")
                
            logger.info("✅ Supabase catalog update complete!")
            # Remove checkpoint file upon success
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
        except Exception as e:
            logger.error(f"Failed to update Supabase: {e}")

if __name__ == "__main__":
    main()
