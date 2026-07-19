"""
remove_mock_products.py
------------------------
Deletes the 60 mock products (IDs 1-60) from local_catalog.json,
frontend/src/catalog_fallback.js, and Supabase products table.
"""

import os
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("remove_mocks")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_CATALOG_FILE = os.path.join(BASE_DIR, "backend", "local_catalog.json")
FRONTEND_FALLBACK_FILE = os.path.join(BASE_DIR, "frontend", "src", "catalog_fallback.js")

def main():
    # 1. Read local_catalog.json
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error(f"Catalog file not found: {LOCAL_CATALOG_FILE}")
        return

    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    original_len = len(catalog)
    # Filter out IDs <= 60
    filtered_catalog = [p for p in catalog if p["id"] > 60]
    filtered_len = len(filtered_catalog)

    logger.info(f"Loaded catalog with {original_len} products. Filtered down to {filtered_len} products.")

    # 2. Save filtered local_catalog.json
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(filtered_catalog, f, indent=4)
    logger.info("Saved filtered local_catalog.json.")

    # 3. Rewrite frontend/src/catalog_fallback.js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(filtered_catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info("Rewrote frontend fallback file.")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # 4. Clean up Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Deleting products with ID <= 60...")
            
            res = supabase.table("products").delete().lte("id", 60).execute()
            logger.info(f"Deleted rows from Supabase. Result count: {len(res.data) if res.data else 0}")
            
            # Verify total count in Supabase
            verify_res = supabase.table("products").select("id", count="exact").execute()
            logger.info(f"✅ Supabase now contains {verify_res.count} products.")
        except Exception as e:
            logger.error(f"Failed to clean up Supabase: {e}")
    else:
        logger.warning("Supabase configuration missing, skipping Supabase cleanup.")

if __name__ == "__main__":
    main()
