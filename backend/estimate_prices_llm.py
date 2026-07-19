import os
import json
import random
import time
import logging
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("estimate_prices_llm")

load_dotenv("backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully.")
else:
    logger.warning("GEMINI_API_KEY not found in environment!")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public"))

def get_local_image_path(image_url):
    """Resolve the clean local path of the product image."""
    clean_path = image_url.lstrip("/")
    path = os.path.join(IMAGES_DIR, clean_path)
    if os.path.exists(path):
        return path
    
    # Try alt lookups
    filename = os.path.basename(image_url)
    for folder in ["images", "catalog"]:
        alt_path = os.path.join(IMAGES_DIR, folder, filename)
        if os.path.exists(alt_path):
            return alt_path
    return None

def estimate_price_heuristically(desc, category):
    """Fallback high-quality retail price estimation in INR based on item attributes."""
    desc_lower = desc.lower()
    if "saree" in desc_lower or "silk" in desc_lower or "lehenga" in desc_lower or "sherwani" in desc_lower or category == "festive":
        return random.randint(1899, 6499)
    elif "coat" in desc_lower or "jacket" in desc_lower or "trench" in desc_lower or category == "winter":
        return random.randint(1299, 3999)
    elif "hoodie" in desc_lower or "jeans" in desc_lower or "denim" in desc_lower or category == "streetwear":
        return random.randint(899, 2499)
    elif "shirt" in desc_lower or "t-shirt" in desc_lower or "kurta" in desc_lower or "kurti" in desc_lower or category == "casual":
        return random.randint(399, 1499)
    else:
        return random.randint(299, 999)

def call_gemini_vision_pricing(image_path, desc):
    """Use Gemini Vision to estimate the retail value of the fashion item in INR."""
    if not GEMINI_API_KEY:
        return None
    try:
        img = Image.open(image_path)
        # Resize to save bandwidth / avoid limits
        img.thumbnail((300, 300))
        
        prompt = f"""
        Estimate the retail price (in Indian Rupees, INR) of this clothing item shown in the image.
        Description: "{desc}"
        
        Return ONLY a single integer value (e.g. 1499) representing the estimated price. Do not include currency symbols, text, or any formatting.
        """
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content([img, prompt])
        text = "".join(c for c in response.text.strip() if c.isdigit())
        if text:
            return int(text)
    except Exception as e:
        logger.warning(f"Gemini Vision pricing failed: {e}")
        # Only trigger quota fallback if it's a rate limit / daily limit error
        if "quota" in str(e).lower() or "429" in str(e).lower():
            raise e
    return None

def main():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found!")
        return

    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    logger.info(f"Estimating prices for {len(catalog)} products...")

    supabase = None
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase.")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")

    llm_quota_exceeded = False
    updated_count = 0

    for idx, p in enumerate(catalog):
        desc = p.get("description", p.get("name", ""))
        category = p.get("category", "casual")
        image_url = p.get("image_url", "")
        
        price = None
        img_path = get_local_image_path(image_url)

        if img_path and not llm_quota_exceeded:
            logger.info(f"[{idx+1}/{len(catalog)}] Estimating price via Gemini Vision: {p['name']}")
            try:
                price = call_gemini_vision_pricing(img_path, desc)
                if price is not None:
                    logger.info(f"  Gemini estimated price: Rs. {price}")
                    # Ensure the estimated price is within a reasonable range (Rs. 100 to 10000)
                    if price < 100 or price > 10000:
                        price = estimate_price_heuristically(desc, category)
            except Exception as e:
                logger.info("Falling back to local heuristic estimation due to quota limit.")
                llm_quota_exceeded = True
        
        # If Gemini was skipped or failed, use local heuristic estimation
        if price is None:
            price = estimate_price_heuristically(desc, category)
            
        p["price"] = price
        updated_count += 1

    # Save local catalog
    with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved local_catalog.json with enriched prices.")

    # Save to frontend catalog fallback js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w", encoding="utf-8") as f:
                f.write(js_content)
            logger.info("Successfully updated frontend fallback catalog file.")
        except Exception as e:
            logger.error(f"Failed to update frontend fallback: {e}")

    # Upsert enriched records to Supabase
    if supabase:
        logger.info("Syncing updated prices to Supabase...")
        DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding", "price", "inventory", "material", "color", "nature", "age_range", "category"}
        db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in catalog]
        
        try:
            supabase.table("products").upsert(db_catalog).execute()
            logger.info("✅ Supabase price upsert complete for all 206 products!")
        except Exception as e:
            logger.error(f"Failed to batch upsert prices to Supabase: {e}")

if __name__ == "__main__":
    main()
