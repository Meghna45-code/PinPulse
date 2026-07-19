import os
import json
import random
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("enrich_catalog_fields")

load_dotenv("backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully.")
else:
    logger.warning("GEMINI_API_KEY not found. LLM calls will be skipped (local fallback only).")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

def extract_fields_locally(desc):
    desc_lower = desc.lower()
    
    # 1. Material
    material = None
    for m in ["silk", "cotton", "linen", "wool", "velvet", "denim", "suede", "leather", "fleece", "rayon", "polyester", "brass", "gold", "silver"]:
        if m in desc_lower:
            material = m.capitalize()
            break
    
    # 2. Color
    color = None
    colors = ["red", "crimson", "maroon", "burgundy", "blue", "navy", "royal blue", "green", "emerald", "mint", "yellow", "saffron", "gold", "pink", "orange", "black", "white", "cream", "beige", "charcoal", "grey", "silver", "tan", "brown", "purple", "amethyst"]
    for c in colors:
        if c in desc_lower:
            color = c.capitalize()
            break
            
    # 3. Nature
    nature = None
    if any(x in desc_lower for x in ["wedding", "bride", "groom", "festive", "festival", "traditional", "puja", "chariot", "rituals", "celebration", "engagement", "ceremony"]):
        nature = "festive"
    elif any(x in desc_lower for x in ["formal", "office", "tuxedo", "suit", "blazer", "workwear", "corporate"]):
        nature = "formal"
    elif any(x in desc_lower for x in ["casual", "daily", "dailywear", "breeze", "summer", "beach"]):
        nature = "casual"
        
    # 4. Age Range
    age_range = None
    if any(x in desc_lower for x in ["college", "musician", "street style", "modern", "fusion", "trendy", "indie", "student"]):
        age_range = "Gen Z"
    elif any(x in desc_lower for x in ["traditional", "ethnic", "wedding", "saree", "sherwani", "bridal"]):
        age_range = "Millennial"
        
    return material, color, nature, age_range

def call_gemini_llm(desc):
    """Fallback LLM text call to predict missing metadata categories from product description."""
    if not GEMINI_API_KEY:
        return {}
    prompt = f"""
    Analyze the following product description and identify:
    1. material (e.g. Silk, Cotton, Linen, Wool, Velvet, Denim, Leather, Polyester)
    2. color (dominant color name, e.g. Red, Blue, Black, Pink, Gold, Green)
    3. nature (vibe/suitability: must be one of 'casual', 'formal', 'festive')
    4. age_range (must be one of 'Gen Z', 'Millennial')

    Description: "{desc}"
    
    Return ONLY a valid JSON object matching this format (no markdown, no backticks):
    {{
      "material": "fabric name",
      "color": "color name",
      "nature": "nature style",
      "age_range": "age demographic"
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini API text call failed: {e}")
        return {}

def main():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found!")
        return

    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    logger.info(f"Processing {len(catalog)} catalog products for database column enrichment...")

    supabase = None
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase.")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")

    updated_count = 0
    for idx, p in enumerate(catalog):
        desc = p.get("description", "")
        
        # 1. Price & Inventory (always set random numbers between 1 and 50)
        p["price"] = random.randint(1, 50)
        p["inventory"] = random.randint(1, 50)
        
        # 2. Extract material, color, nature, age_range
        loc_mat, loc_col, loc_nat, loc_age = extract_fields_locally(desc)
        
        # Apply local rules directly
        p["material"] = p.get("material") or loc_mat or "Cotton"
        p["color"] = p.get("color") or loc_col or "Multi"
        p["nature"] = p.get("nature") or loc_nat or "casual"
        p["age_range"] = p.get("age_range") or loc_age or "Millennial"

        # Ensure all columns are properly capitalised/normalised
        p["material"] = str(p["material"]).strip().capitalize()
        p["color"] = str(p["color"]).strip().capitalize()
        p["nature"] = str(p["nature"]).strip().lower()
        p["age_range"] = str(p["age_range"]).strip()
        p["category"] = str(p.get("category", "casual")).strip().lower()

        updated_count += 1

    # Save local catalog
    with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)
    logger.info(f"Saved enriched local_catalog.json.")

    # Save to frontend catalog fallback js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w", encoding="utf-8") as f:
                f.write(js_content)
            logger.info("Successfully updated frontend fallback catalog file.")
        except Exception as e:
            logger.error(f"Failed to update frontend fallback: {e}")

    # Upsert fully enriched records to Supabase
    if supabase:
        logger.info("Syncing enriched catalog columns to Supabase...")
        DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding", "price", "inventory", "material", "color", "nature", "age_range", "category"}
        db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in catalog]
        
        try:
            # Perform batch upsert
            supabase.table("products").upsert(db_catalog).execute()
            logger.info("✅ Supabase batch upsert complete for all 206 products!")
        except Exception as e:
            logger.error(f"Failed to batch upsert to Supabase: {e}")

if __name__ == "__main__":
    main()
