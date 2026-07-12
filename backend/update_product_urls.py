import os
import json
import logging
import urllib.parse
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("update_product_urls")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

def update_urls():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found.")
        return

    # 1. Read existing catalog
    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    logger.info(f"Loaded {len(catalog)} products for URL updating...")

    # 2. Assign search URLs for items missing them
    updated_count = 0
    for p in catalog:
        url = p.get("product_url", "")
        # Check if URL is missing, empty, or a generic placeholder
        if not url or url.strip() == "" or "placeholder" in url.lower():
            name = p["name"]
            # Encode name to create a valid Myntra search link
            encoded_name = urllib.parse.quote_plus(name)
            search_url = f"https://www.myntra.com/search?q={encoded_name}"
            p["product_url"] = search_url
            updated_count += 1

    logger.info(f"Assigned search-based Myntra store links to {updated_count} products.")

    # 3. Save clean catalog locally
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved local_catalog.json")

    # 4. Save to frontend fallback
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info(f"Rewrote frontend fallback file: {FRONTEND_FALLBACK_FILE}")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # 5. Sync to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Updating 'product_url' column...")
            
            for p in catalog:
                pid = p["id"]
                p_url = p["product_url"]
                supabase.table("products").update({"product_url": p_url}).eq("id", pid).execute()
                
            logger.info("✅ Successfully updated all product URLs in Supabase products table!")
        except Exception as e:
            logger.error(f"Failed to update Supabase: {e}")
    else:
        logger.warning("Supabase credentials missing. Local updates complete.")

if __name__ == "__main__":
    update_urls()
