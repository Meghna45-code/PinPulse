"""
update_local_image_urls.py
--------------------------
Updates local_catalog.json to point product image_url fields to local
images served from the Vite dev server at /images/<id>.<ext>.

Products with IDs 1-100 get a local URL.
Products with IDs 101-159 keep their existing Unsplash URLs.
Also updates the Supabase database if credentials are available.
"""
import os
import json
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("update_images")

# Resolve paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_FILE = os.path.join(BASE_DIR, "backend", "local_catalog.json")
IMAGES_DIR = os.path.join(BASE_DIR, "Pictures of fashion apparel 2")
ENV_PATH = os.path.join(BASE_DIR, "backend", ".env")

load_dotenv(ENV_PATH)

def build_image_map():
    """Returns {id_number: filename} from the images folder."""
    img_map = {}
    for fname in os.listdir(IMAGES_DIR):
        name_no_ext = os.path.splitext(fname)[0]
        try:
            num = int(name_no_ext)
            img_map[num] = fname
        except ValueError:
            pass
    return img_map

def get_local_image_url(product_id: int, img_map: dict) -> str | None:
    """Returns the /images/<filename> URL for a product, or None if no local image exists."""
    fname = img_map.get(product_id)
    if fname:
        return f"/images/{fname}"
    return None

def update_catalog():
    img_map = build_image_map()
    logger.info(f"Found {len(img_map)} local images for IDs: {sorted(img_map.keys())[:5]}...")

    with open(CATALOG_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    updated_count = 0
    for p in products:
        local_url = get_local_image_url(p["id"], img_map)
        if local_url:
            old_url = p.get("image_url", "")
            if old_url != local_url:
                p["image_url"] = local_url
                updated_count += 1

    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    logger.info(f"Updated image_url for {updated_count} products in local_catalog.json.")
    return products

def update_supabase(products):
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase credentials not found. Skipping DB update.")
        return

    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Connected to Supabase.")

        img_map = build_image_map()
        to_update = [p for p in products if p["id"] in img_map]

        logger.info(f"Updating {len(to_update)} products in Supabase with local image URLs...")

        # Batch update in chunks
        chunk_size = 20
        for i in range(0, len(to_update), chunk_size):
            chunk = to_update[i:i + chunk_size]
            for p in chunk:
                supabase.table("products") \
                    .update({"image_url": p["image_url"]}) \
                    .eq("id", p["id"]) \
                    .execute()
            logger.info(f"  Updated chunk {i // chunk_size + 1} ({len(chunk)} products).")

        logger.info("Supabase update complete.")
    except Exception as e:
        logger.error(f"Failed to update Supabase: {e}")

if __name__ == "__main__":
    products = update_catalog()
    update_supabase(products)
    print("\n✅ Done! local_catalog.json updated with local image URLs.")
    print("   Products 1-100 now point to /images/<id>.<ext>")
    print("   Products 101-159 keep their Unsplash URLs.\n")
