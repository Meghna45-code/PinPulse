import os
import sys
import json
import logging
import pandas as pd
from embed_catalog import get_vibe_vector, upload_to_supabase, LOCAL_CATALOG_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("import_excel")


def infer_tags(desc):
    """Infer fashion tags from a product description string."""
    desc_lower = desc.lower()
    tags = set()

    # ── Ethnic / Traditional ──────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "saree", "kurta", "lehenga", "ethnic", "traditional", "sherwani",
        "kasavu", "jainsem", "jymphong", "mundu", "nehru", "salwar", "suit",
        "kurti", "dhoti", "dupatta", "pattu", "pavada", "anklet"
    ]):
        tags.update(["ethnic", "traditional"])

    # ── Casual / Everyday ─────────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "casual", "shirt", "tee", "jeans", "co-ord", "linen coord",
        "printed shirt", "shorts", "beachwear"
    ]):
        tags.update(["casual"])

    # ── Events ────────────────────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "wedding", "sangeet", "pheras", "ceremony", "bridal", "reception",
        "engagement", "thalikettu", "vidaai"
    ]):
        tags.update(["ceremonial", "festive"])
    if any(x in desc_lower for x in [
        "festive", "diwali", "chhath", "onam", "vishu", "eid", "christmas",
        "puja", "holi", "biennale", "carnival", "harvest", "cherry blossom",
        "republic day", "independence day", "boat race"
    ]):
        tags.update(["festive"])
    if any(x in desc_lower for x in ["party", "evening gown", "gown", "tuxedo", "reception"]):
        tags.update(["party", "formal"])
    if any(x in desc_lower for x in ["civic", "office", "formal", "blazer", "suit", "tuxedo"]):
        tags.update(["formal", "western_formal"])

    # ── Weather ───────────────────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "cotton", "linen", "summer", "breathable", "lightweight",
        "bohemian", "coastal", "beachwear", "breathable cotton"
    ]):
        tags.update(["summer", "breathable", "casual"])
    if any(x in desc_lower for x in [
        "winter", "velvet", "coat", "jacket", "woolen", "sweater", "warm",
        "trench", "overcoat", "beanie", "scarf", "shawl", "pashmina",
        "fleece", "wool", "leather jacket"
    ]):
        tags.update(["winter", "warm", "heavy-weight"])

    # ── Streetwear / Modern ───────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "denim", "hoodie", "streetwear", "boots", "modern", "fusion", "trendy",
        "indo-western", "bohemian", "artsy", "indie", "oversized", "hoodie",
        "ankle boots", "street style", "street wear", "boho"
    ]):
        tags.update(["streetwear", "modern", "fusion"])

    # ── Accessories ───────────────────────────────────────────────────────────
    if any(x in desc_lower for x in [
        "earring", "necklace", "anklet", "ring", "sunglasses", "tote bag",
        "handbag", "watch", "bangles", "bracelet", "statement"
    ]):
        tags.update(["accessories"])

    # ── Regional Strict Rules ─────────────────────────────────────────────────
    if "banarasi" in desc_lower or "heavy silk" in desc_lower or "heavy red" in desc_lower:
        tags.update(["heavy_silk", "silk", "ceremonial", "ethnic", "traditional"])
    if "kasavu" in desc_lower or "kerala wedding" in desc_lower or "mundu" in desc_lower:
        tags.update(["kasavu_weave", "white", "gold", "ethnic"])
    if any(x in desc_lower for x in ["jainsem", "jymphong", "tribal", "khasi", "handwoven"]):
        tags.update(["handwoven_silk", "tribal_heritage", "ethnic"])
    if any(x in desc_lower for x in ["chhath", "chhath puja"]):
        tags.update(["saffron", "yellow", "patna", "chhath-puja", "cotton"])
    if "pastel" in desc_lower:
        tags.update(["pastel", "semi-ethnic"])
    if any(x in desc_lower for x in ["silk", "zari", "embroidered", "embellished", "sequin"]):
        tags.update(["silk", "festive"])
    if any(x in desc_lower for x in ["velvet gown", "evening gown", "black velvet"]):
        tags.update(["party", "festive", "velvet"])
    if "lehenga" in desc_lower or "mint green" in desc_lower or "fusion lehenga" in desc_lower:
        tags.update(["ethnic", "festive", "fusion", "semi-ethnic"])
    if any(x in desc_lower for x in ["linen", "bohemian", "boho", "biennale"]):
        tags.update(["casual", "summer", "breathable", "sustainable", "modern"])

    return list(tags)


def make_category(tags):
    """Derive the UI category string from inferred tags."""
    if "heavy_silk" in tags or "kasavu_weave" in tags or "tribal_heritage" in tags:
        return "festive"
    if "ceremonial" in tags or ("festive" in tags and "ethnic" in tags):
        return "festive"
    if "winter" in tags or "velvet" in tags or "heavy-weight" in tags:
        return "winter"
    if "streetwear" in tags or "modern" in tags or "fusion" in tags:
        return "streetwear"
    return "casual"


def make_product(pid, desc, url, catalog_size):
    """Build a single product dict."""
    desc = desc.strip()
    url  = url.strip() if url else ""
    tags = infer_tags(desc)
    vector = get_vibe_vector(tags)

    # Name: first 5 words, capitalised
    name = " ".join(desc.split()[:5]).strip().capitalize()
    if len(name) < 5:
        name = desc[:40]

    return {
        "id":          pid,
        "name":        name,
        "description": desc,
        "category":    make_category(tags),
        "image_url":   f"/catalog/catalog_{pid % 60 + 1}.jpg",
        "product_url": url,
        "tags":        tags,
        "zip_codes":   [],
        "embedding":   vector,
    }


def parse_sheet1(df):
    """Sheet1 format: col0=URL, col1=description (20 rows)."""
    rows = []
    for _, row in df.iterrows():
        url  = str(row[0]).strip()
        desc = str(row[1]).strip()
        if desc and url.startswith("http"):
            rows.append((desc, url))
    return rows


def parse_sheet3(df):
    """Sheet3 format: col0=description, col1=URL1, col2=URL2 (50 desc groups × 2 urls)."""
    rows = []
    current_desc = None
    for _, row in df.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
        col2 = str(row[2]).strip() if pd.notna(row[2]) else ""

        # A new description row (non-URL in col0)
        if col0 and not col0.startswith("http"):
            current_desc = col0

        if current_desc:
            if col1.startswith("http"):
                rows.append((current_desc, col1))
            if col2.startswith("http"):
                rows.append((current_desc, col2))
    return rows


def import_excel(excel_filename="Fashion Apparel.xlsx"):
    excel_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", excel_filename))
    logger.info(f"Reading: {excel_path}")

    if not os.path.exists(excel_path):
        logger.error(f"File not found: {excel_path}")
        return

    # Load existing catalog
    if not os.path.exists(LOCAL_CATALOG_FILE):
        logger.error("local_catalog.json not found. Run embed_catalog.py first.")
        return

    with open(LOCAL_CATALOG_FILE, "r") as f:
        catalog = json.load(f)

    existing_urls = {p.get("product_url", "") for p in catalog}
    next_id = max(p["id"] for p in catalog) + 1 if catalog else 1

    # ── Read all sheets ────────────────────────────────────────────────────────
    xl = pd.ExcelFile(excel_path)
    all_pairs = []   # list of (desc, url) tuples

    for sheet in xl.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        logger.info(f"  Sheet '{sheet}': {len(df)} rows × {df.shape[1]} cols")

        # Check if column 0 contains URLs to determine format type dynamically
        first_col_is_url = False
        for val in df[0].dropna():
            val_str = str(val).strip()
            if val_str.startswith("http"):
                first_col_is_url = True
                break

        if first_col_is_url:
            # Original format: col0=URL, col1=desc
            pairs = parse_sheet1(df)
        elif df.shape[1] >= 3:
            # New format: col0=desc, col1=URL1, col2=URL2
            pairs = parse_sheet3(df)
        else:
            logger.warning(f"  Sheet '{sheet}' has unexpected column count ({df.shape[1]}), skipping.")
            continue

        logger.info(f"  Parsed {len(pairs)} (desc, url) pairs from sheet '{sheet}'.")
        all_pairs.extend(pairs)

    # ── Deduplicate & build products ──────────────────────────────────────────
    new_products = []
    skipped_dupes = 0

    for desc, url in all_pairs:
        if url in existing_urls:
            skipped_dupes += 1
            continue
        p = make_product(next_id, desc, url, len(catalog) + len(new_products))
        new_products.append(p)
        existing_urls.add(url)
        next_id += 1

    if not new_products:
        logger.info(f"No new products to add (skipped {skipped_dupes} duplicates).")
        return

    catalog.extend(new_products)

    # Save local catalog (keep all fields including 'category' for the frontend)
    with open(LOCAL_CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=4)

    logger.info(
        f"Added {len(new_products)} new products "
        f"(skipped {skipped_dupes} duplicates). "
        f"Total catalog size: {len(catalog)}."
    )
    logger.info("Uploading full catalog to Supabase...")

    # Supabase products table only has these columns — strip any extras
    DB_FIELDS = {"id", "name", "description", "image_url", "product_url", "tags", "zip_codes", "embedding"}
    db_catalog = [{k: v for k, v in p.items() if k in DB_FIELDS} for p in catalog]

    success = upload_to_supabase(db_catalog)
    if success:
        logger.info("✅ Supabase upload complete!")
    else:
        logger.error("❌ Supabase upload failed.")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "Fashion Apparel.xlsx"
    import_excel(filename)
