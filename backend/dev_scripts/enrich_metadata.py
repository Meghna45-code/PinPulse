"""
enrich_metadata.py
------------------
Populates and normalises all product metadata fields locally (without LLM quota dependency)
and pushes the fully enriched table to Supabase.
"""

import os
import json
import random
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("enrich_metadata")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOCAL_CATALOG_FILE = os.path.join(BASE_DIR, "backend", "local_catalog.json")
FRONTEND_FALLBACK_FILE = os.path.join(BASE_DIR, "frontend", "src", "catalog_fallback.js")

def extract_fields_locally(desc, category):
    desc_lower = desc.lower()
    
    # 1. Material
    material = "Cotton"
    for m in ["silk", "cotton", "linen", "wool", "velvet", "denim", "suede", "leather", "fleece", "rayon", "polyester", "georgette", "chiffon", "brass", "gold", "silver"]:
        if m in desc_lower:
            material = m.capitalize()
            break
            
    # 2. Color
    color = "Multi"
    colors = ["red", "crimson", "maroon", "burgundy", "blue", "navy", "royal blue", "green", "emerald", "mint", "yellow", "saffron", "gold", "pink", "orange", "black", "white", "cream", "beige", "charcoal", "grey", "silver", "tan", "brown", "purple", "mustard"]
    for c in colors:
        if c in desc_lower:
            color = c.capitalize()
            break
            
    # 3. Nature (Aesthetic style)
    nature = "casual"
    if any(x in desc_lower for x in ["wedding", "bride", "groom", "festive", "festival", "traditional", "puja", "chariot", "rituals", "celebration", "engagement", "ceremony"]):
        nature = "festive"
    elif any(x in desc_lower for x in ["formal", "office", "tuxedo", "suit", "blazer", "workwear", "corporate"]):
        nature = "formal"
    elif any(x in desc_lower for x in ["casual", "daily", "dailywear", "breeze", "summer", "beach", "hoodie", "sweatshirt"]):
        nature = "casual"
    elif category == "streetwear":
        nature = "casual"
        
    # 4. Age Group / Demographic
    # Must be 'gen-z' or 'millennial'
    age_group = "millennial"
    if any(x in desc_lower for x in ["college", "musician", "street style", "modern", "fusion", "trendy", "indie", "student", "hoodie", "sweatshirt", "cargo", "streetwear"]):
        age_group = "gen-z"
    elif category == "streetwear":
        age_group = "gen-z"
        
    return material, color, nature, age_group

def estimate_price_heuristically(desc, category):
    desc_lower = desc.lower()
    if "saree" in desc_lower or "silk" in desc_lower or "lehenga" in desc_lower or "sherwani" in desc_lower or category in ["festive", "ethnic", "traditional"]:
        return random.randint(1899, 6499)
    elif "coat" in desc_lower or "jacket" in desc_lower or "trench" in desc_lower or category == "winter":
        return random.randint(1299, 3999)
    elif "hoodie" in desc_lower or "jeans" in desc_lower or "denim" in desc_lower or category == "streetwear":
        return random.randint(899, 2499)
    elif "shirt" in desc_lower or "t-shirt" in desc_lower or "kurta" in desc_lower or "kurti" in desc_lower or category == "casual":
        return random.randint(399, 1499)
    else:
        return random.randint(299, 999)

def main():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found!")
        return

    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    logger.info(f"Enriching metadata fields for {len(catalog)} products...")

    for p in catalog:
        desc = p.get("description", "")
        category = p.get("category", "casual").lower()

        # Extract material, color, nature, and demographic age group
        mat, col, nat, age = extract_fields_locally(desc, category)
        
        p["material"] = mat
        p["color"] = col
        p["nature"] = nat
        # Store in age_range column
        p["age_range"] = "Gen Z" if age == "gen-z" else "Millennial"
        p["category"] = category
        p["price"] = estimate_price_heuristically(desc, category)
        p["inventory"] = random.randint(10, 80)

    # Save local catalog
    with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved local_catalog.json.")

    # Save to frontend catalog fallback
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w", encoding="utf-8") as f:
                f.write(js_content)
            logger.info("Successfully updated frontend fallback catalog file.")
        except Exception as e:
            logger.error(f"Failed to update frontend fallback: {e}")

    # Upsert enriched records to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Syncing enriched fields...")

            DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding", "price", "inventory", "material", "color", "nature", "age_range", "category"}
            db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in catalog]

            supabase.table("products").upsert(db_catalog).execute()
            logger.info("✅ Supabase batch upsert complete for all products!")
        except Exception as e:
            logger.error(f"Failed to batch upsert to Supabase: {e}")
    else:
        logger.warning("Supabase credentials missing, skipping DB sync.")

if __name__ == "__main__":
    main()
