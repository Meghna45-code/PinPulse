import os
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("deduplicate_catalog")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

def deduplicate():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found.")
        return

    # 1. Read existing catalog
    with open(LOCAL_CATALOG_FILE, "r") as f:
        products = json.load(f)

    logger.info(f"Loaded {len(products)} products from local catalog.")

    # 2. Filter out duplicates
    seen = set()
    clean_products = []
    
    # Assign consecutive clean IDs starting from 1 to keep things tidy
    next_id = 1
    for p in products:
        key = (p["name"].strip().lower(), p["description"].strip().lower())
        if key not in seen:
            seen.add(key)
            p["id"] = next_id
            clean_products.append(p)
            next_id += 1

    logger.info(f"Deduplicated to {len(clean_products)} unique products.")

    # 3. Save clean catalog locally
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(clean_products, f, indent=4)
    logger.info("Saved deduplicated local_catalog.json")

    # 4. Save clean catalog to frontend fallback
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(clean_products, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info(f"Rewrote clean frontend fallback: {FRONTEND_FALLBACK_FILE}")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # 5. Clear and upload to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            
            logger.info("Connected to Supabase. Clearing 'products' table...")
            # We can delete all rows by matching id > 0
            supabase.table("products").delete().neq("id", 0).execute()
            logger.info("Cleared 'products' table in Supabase.")
            
            logger.info("Uploading deduplicated clean catalog to Supabase...")
            # Supabase products table schema fields
            DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding"}
            db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in clean_products]
            
            # Batch upload in chunks of 50
            chunk_size = 50
            for i in range(0, len(db_catalog), chunk_size):
                chunk = db_catalog[i:i+chunk_size]
                supabase.table("products").insert(chunk).execute()
                logger.info(f"Uploaded chunk {i//chunk_size + 1}/{(len(db_catalog)-1)//chunk_size + 1}")
                
            logger.info("✅ Supabase deduplication sync complete!")
        except Exception as e:
            logger.error(f"Failed to update Supabase: {e}")
    else:
        logger.warning("Supabase credentials missing. Local deduplication complete.")

if __name__ == "__main__":
    deduplicate()
