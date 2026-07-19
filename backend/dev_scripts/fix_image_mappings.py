"""
fix_image_mappings.py
---------------------
Maps local images in frontend/public/images/ to products 61-207.
- IDs 61-160 (from Fashion Apparel.xlsx) map to Pictures of fashion apparel 2 (images 1 to 100).
- IDs 161-207 (from Fashion Apparel2.xlsx) map to Pictures of fashion apparel (images 101 to 200).
"""

import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fix_images")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOCAL_CATALOG_FILE = os.path.join(BASE_DIR, "backend", "local_catalog.json")
FRONTEND_FALLBACK_FILE = os.path.join(BASE_DIR, "frontend", "src", "catalog_fallback.js")
IMAGES_DIR = os.path.join(BASE_DIR, "frontend", "public", "images")

EXCEL1_PATH = os.path.join(BASE_DIR, "excel_sheets", "Fashion Apparel.xlsx")
EXCEL2_PATH = os.path.join(BASE_DIR, "excel_sheets", "Fashion Apparel2.xlsx")

def get_image_file(prefix):
    """Finds a file in frontend/public/images/ starting with the given prefix."""
    if not os.path.exists(IMAGES_DIR):
        return None
    prefix_str = str(prefix).lower()
    for fname in os.listdir(IMAGES_DIR):
        name_no_ext = os.path.splitext(fname)[0].lower()
        if name_no_ext == prefix_str:
            return fname
    return None

def main():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error(f"Catalog file not found: {LOCAL_CATALOG_FILE}")
        return

    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    # 1. Build URL-to-index mapping for Sheet3 of Excel 2 (Fashion Apparel2.xlsx)
    # Sheet3 format: col0=description, col1=URL1, col2=URL2
    excel2_map = {}
    if os.path.exists(EXCEL2_PATH):
        df2 = pd.read_excel(EXCEL2_PATH, sheet_name="Sheet3", header=None)
        current_desc = None
        group_index = -1
        for _, row in df2.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
            col2 = str(row[2]).strip() if pd.notna(row[2]) else ""

            if col0 and not col0.startswith("http"):
                current_desc = col0
                group_index += 1

            if current_desc and group_index >= 0:
                if col1.startswith("http"):
                    img_num = 100 + (2 * group_index + 1)
                    excel2_map[col1.strip().lower()] = img_num
                if col2.startswith("http"):
                    img_num = 100 + (2 * group_index + 2)
                    excel2_map[col2.strip().lower()] = img_num
        logger.info(f"Parsed {len(excel2_map)} URLs from Excel 2 sheet3.")
    else:
        logger.error(f"Excel 2 not found at {EXCEL2_PATH}")

    # 2. Map images for each product in catalog
    updated_count = 0
    for p in catalog:
        pid = p["id"]
        url = p.get("product_url", "").strip().lower()
        new_url = None

        if 61 <= pid <= 160:
            # First Excel sheet product (corresponds to local images 1 to 100)
            img_num = pid - 60
            fname = get_image_file(img_num)
            if fname:
                new_url = f"/images/{fname}"
            else:
                logger.warning(f"No local image found for ID {pid} (expected prefix: {img_num})")

        elif pid >= 161:
            # Second Excel sheet product (corresponds to local images 101 to 200)
            img_num = excel2_map.get(url)
            if img_num:
                fname = get_image_file(img_num)
                if fname:
                    new_url = f"/images/{fname}"
                else:
                    logger.warning(f"No local image found for ID {pid} (expected prefix: {img_num})")
            else:
                logger.warning(f"Product URL not found in Excel 2 map: ID {pid}, URL {url}")

        if new_url:
            old_url = p.get("image_url", "")
            if old_url != new_url:
                p["image_url"] = new_url
                updated_count += 1

    logger.info(f"Updated {updated_count} image URLs in catalog.")

    # 3. Save local_catalog.json
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved local_catalog.json.")

    # 4. Rewrite frontend/src/catalog_fallback.js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info("Rewrote frontend fallback file.")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend fallback: {e}")

    # 5. Sync to Supabase
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Updating image_urls...")
            
            # Batch update in chunks
            chunk_size = 20
            for i in range(0, len(catalog), chunk_size):
                chunk = catalog[i:i + chunk_size]
                for p in chunk:
                    supabase.table("products") \
                        .update({"image_url": p["image_url"]}) \
                        .eq("id", p["id"]) \
                        .execute()
                logger.info(f"  Updated chunk {i // chunk_size + 1} ({len(chunk)} products).")
                
            logger.info("✅ Supabase image sync complete!")
        except Exception as e:
            logger.error(f"Failed to sync images with Supabase: {e}")
    else:
        logger.warning("Supabase credentials missing, skipping DB sync.")

if __name__ == "__main__":
    main()
