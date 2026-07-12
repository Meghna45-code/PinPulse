import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("map_excel_urls")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
EXCEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Fashion Apparel.xlsx"))

def map_urls():
    if not os.path.exists(EXCEL_FILE):
        logger.error(f"Excel file not found at: {EXCEL_FILE}")
        return
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error(f"Local catalog not found at: {LOCAL_CATALOG_FILE}")
        return

    # 1. Read Excel rows
    xl = pd.ExcelFile(EXCEL_FILE)
    excel_products = [] # list of dicts: {"url": ..., "desc": ...}
    for sheet in xl.sheet_names:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=None)
        if df.shape[1] == 2:
            for _, row in df.iterrows():
                url = str(row[0]).strip()
                desc = str(row[1]).strip()
                if desc and url.startswith("http"):
                    excel_products.append({"url": url, "desc": desc.lower()})
        elif df.shape[1] >= 3:
            # col0=desc, col1=url1, col2=url2
            for _, row in df.iterrows():
                desc = str(row[0]).strip() if pd.notna(row[0]) else ""
                url1 = str(row[1]).strip() if pd.notna(row[1]) else ""
                url2 = str(row[2]).strip() if pd.notna(row[2]) else ""
                if desc:
                    if url1.startswith("http"):
                        excel_products.append({"url": url1, "desc": desc.lower()})
                    if url2.startswith("http"):
                        excel_products.append({"url": url2, "desc": desc.lower()})

    logger.info(f"Loaded {len(excel_products)} real product links from Excel.")

    # 2. Load catalog
    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    # 3. Perform semantic fallback mapping for first 60 items
    mapped_count = 0
    for p in catalog:
        pid = p["id"]
        # Only overwrite if it's a mock product (1 to 60) or currently has a search query URL
        url = p.get("product_url", "")
        if pid <= 60 or "search?q=" in url:
            name_lower = p["name"].lower()
            desc_lower = p["description"].lower()
            category = p.get("category", "")
            
            # Find the best match in Excel products
            best_match_url = None
            best_score = -1
            
            for ep in excel_products:
                ep_desc = ep["desc"]
                # Calculate word overlap score
                words_p = set(name_lower.split() + desc_lower.split())
                words_ep = set(ep_desc.split())
                score = len(words_p.intersection(words_ep))
                
                # Boost if category keyword aligns
                if category == "festive" and ("saree" in ep_desc or "lehenga" in ep_desc or "sherwani" in ep_desc or "kurta" in ep_desc):
                    score += 2
                elif category == "winter" and ("coat" in ep_desc or "jacket" in ep_desc or "sweatshirt" in ep_desc or "sweater" in ep_desc):
                    score += 2
                elif category == "streetwear" and ("hoodie" in ep_desc or "streetwear" in ep_desc or "cargo" in ep_desc):
                    score += 2
                    
                if score > best_score:
                    best_score = score
                    best_match_url = ep["url"]
                    
            if best_match_url:
                p["product_url"] = best_match_url
                mapped_count += 1

    logger.info(f"Mapped {mapped_count} products to exact Excel product URLs.")

    # 4. Save locally
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)
    logger.info("Saved local_catalog.json")

    # 5. Save to frontend
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info(f"Rewrote frontend fallback file: {FRONTEND_FALLBACK_FILE}")
        except Exception as e:
            logger.error(f"Failed to rewrite frontend: {e}")

    # 6. Sync to Supabase
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
        logger.warning("Supabase credentials missing. Skipping remote sync.")

if __name__ == "__main__":
    map_urls()
