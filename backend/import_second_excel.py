import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("import_second_excel")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
EXCEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "excel_sheets", "Fashion Apparel2.xlsx"))

# Import semantic image mapping function from update_real_images
from update_real_images import find_best_semantic_image

# Mock vibe vector generator from import_excel
def infer_tags(desc):
    tags = []
    desc_lower = desc.lower()
    
    # Material
    for t in ["silk", "cotton", "linen", "velvet", "woolen", "suede", "leather", "denim", "cashmere", "pashmina", "georgette"]:
        if t in desc_lower:
            tags.append(t)
            
    # Aesthetic / Type
    for t in ["saree", "sherwani", "kurta", "lehenga", "gown", "suit", "jacket", "coat", "hoodie", "sweater", "cardigan", "shirt", "tee", "jeans", "pants", "shorts", "waistcoat", "jymphong", "jainsem", "shawl", "dupatta", "doti", "dhoti"]:
        if t in desc_lower:
            tags.append(t)
            
    # Occasion / Surge keywords
    if "wedding" in desc_lower or "bridal" in desc_lower or "groom" in desc_lower or "vivah" in desc_lower or "marriage" in desc_lower or "pheras" in desc_lower or "reception" in desc_lower or "engagement" in desc_lower:
        tags.append("ceremonial")
    if "puja" in desc_lower or "festive" in desc_lower or "mela" in desc_lower or "vrat" in desc_lower or "traditional" in desc_lower or "ethnic" in desc_lower or "kasavu" in desc_lower:
        tags.append("festive")
    if "casual" in desc_lower or "daily" in desc_lower or "breathable" in desc_lower or "summer" in desc_lower:
        tags.append("casual")
    if "street" in desc_lower or "modern" in desc_lower or "youth" in desc_lower or "oversized" in desc_lower:
        tags.append("streetwear")
    if "winter" in desc_lower or "warm" in desc_lower or "cold" in desc_lower:
        tags.append("winter")
        
    return list(set(tags))

def get_vibe_vector(tags):
    # Vector simulation based on tags
    import numpy as np
    vec = np.zeros(512)
    # Seed random vector consistently based on tag names
    for t in tags:
        seed = sum(ord(c) for c in t)
        np.random.seed(seed)
        vec += np.random.randn(512) * 0.1
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def make_category(tags):
    if "heavy_silk" in tags or "kasavu_weave" in tags or "festive" in tags or "ceremonial" in tags:
        return "festive"
    if "winter" in tags or "velvet" in tags or "woolen" in tags:
        return "winter"
    if "streetwear" in tags or "modern" in tags or "hoodie" in tags:
        return "streetwear"
    return "casual"

def parse_sheet3(df):
    rows = []
    current_desc = None
    for _, row in df.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
        col2 = str(row[2]).strip() if pd.notna(row[2]) else ""

        # A new description row
        if col0 and not col0.startswith("http"):
            current_desc = col0

        if current_desc:
            if col1.startswith("http"):
                rows.append((current_desc, col1))
            if col2.startswith("http"):
                rows.append((current_desc, col2))
    return rows

def import_second():
    if not os.path.exists(EXCEL_FILE):
        logger.error(f"Excel file not found: {EXCEL_FILE}")
        return
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found.")
        return

    # Load existing catalog
    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)
    logger.info(f"Loaded existing catalog of {len(catalog)} products.")

    existing_urls = {p.get("product_url", "").strip().lower() for p in catalog}
    existing_desc = {p.get("description", "").strip().lower() for p in catalog}
    
    # Read Sheet3
    df = pd.read_excel(EXCEL_FILE, sheet_name="Sheet3", header=None)
    logger.info(f"Read Sheet3: {len(df)} rows")
    pairs = parse_sheet3(df)
    logger.info(f"Parsed {len(pairs)} (desc, url) pairs from Sheet3.")

    # Deduplicate & Build Products
    new_products = []
    skipped_count = 0
    next_id = max(p["id"] for p in catalog) + 1 if catalog else 1

    for desc, url in pairs:
        url_clean = url.strip()
        desc_clean = desc.strip()
        
        # Skip if already exists by url or exact desc
        if url_clean.lower() in existing_urls or desc_clean.lower() in existing_desc:
            skipped_count += 1
            continue
            
        tags = infer_tags(desc_clean)
        category = make_category(tags)
        vector = get_vibe_vector(tags)
        
        # Name formulation
        name = " ".join(desc_clean.split()[:5]).strip().capitalize()
        # Remove any smart quotes or parsing errors from string
        name = name.replace("", "")
        desc_clean = desc_clean.replace("", "")
        
        image_url = find_best_semantic_image(name, desc_clean, category, tags)
        
        p = {
            "id": next_id,
            "name": name,
            "description": desc_clean,
            "category": category,
            "image_url": image_url,
            "product_url": url_clean,
            "tags": tags,
            "zip_codes": [],
            "embedding": vector
        }
        new_products.append(p)
        existing_urls.add(url_clean.lower())
        existing_desc.add(desc_clean.lower())
        next_id += 1

    logger.info(f"Filtered out {skipped_count} duplicates. Adding {len(new_products)} new products.")
    
    if not new_products:
        logger.info("No new unique products to import.")
        return

    # Add to catalog
    catalog.extend(new_products)
    
    # Save clean catalog locally
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
    logger.info(f"Saved local_catalog.json. Total products: {len(catalog)}")

    # Save to frontend
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info("Rewrote frontend fallback file.")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # Upload/Sync to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Clearing products and performing full sync...")
            
            # Wipe table first to avoid any ID constraint issues
            supabase.table("products").delete().neq("id", 0).execute()
            
            DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding"}
            db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in catalog]
            
            chunk_size = 50
            for i in range(0, len(db_catalog), chunk_size):
                chunk = db_catalog[i:i+chunk_size]
                supabase.table("products").insert(chunk).execute()
                logger.info(f"Uploaded chunk {i//chunk_size + 1}/{(len(db_catalog)-1)//chunk_size + 1}")
                
            logger.info("✅ Supabase sync complete for all products!")
        except Exception as e:
            logger.error(f"Failed to sync with Supabase: {e}")

if __name__ == "__main__":
    import_second()
