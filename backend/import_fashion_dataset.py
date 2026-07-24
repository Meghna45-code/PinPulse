import os
import sys
import json
import ast
import re
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector, LOCAL_CATALOG_FILE

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
    tags_set = set(tags)
    if "ethnic" in tags_set or "traditional" in tags_set:
        return "ethnic"
    if "festive" in tags_set or "ceremonial" in tags_set:
        return "festive"
    if "winter" in tags_set or "warm" in tags_set:
        return "winter"
    if "formal" in tags_set or "western_formal" in tags_set:
        return "formal"
    if "streetwear" in tags_set or "modern" in tags_set:
        return "streetwear"
    return "casual"

def clean_html(text):
    if not isinstance(text, str):
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

csv_path = "Fashion Dataset.csv"
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found!")
    sys.exit(1)

print(f"Loading {csv_path}...")
df = pd.read_csv(csv_path)
print(f"Total rows in dataset: {len(df)}")

# Load existing catalog (e.g., M1-M14)
existing_catalog = []
if os.path.exists(LOCAL_CATALOG_FILE):
    with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
        existing_catalog = json.load(f)

print(f"Existing catalog count: {len(existing_catalog)}")
existing_ids = {p["id"] for p in existing_catalog if "id" in p}
next_id = max(existing_ids) + 1 if existing_ids else 1

new_products = []

for idx, row in df.iterrows():
    if pd.isna(row.get("name")) or pd.isna(row.get("img")):
        continue

    p_id_raw = row.get("p_id")
    p_id = int(p_id_raw) if pd.notna(p_id_raw) else next_id

    # Ensure unique ID
    current_id = p_id if p_id not in existing_ids else next_id
    if current_id in existing_ids:
        next_id += 1
        current_id = next_id

    name = str(row["name"]).strip()
    raw_desc = clean_html(str(row.get("description", "")))
    brand = str(row.get("brand", "")).strip() if pd.notna(row.get("brand")) else ""
    colour = str(row.get("colour", "")).strip() if pd.notna(row.get("colour")) else ""
    
    price_val = row.get("price")
    price = int(float(price_val)) if pd.notna(price_val) else 1999

    img_url = str(row["img"]).strip().replace("http://", "https://")

    rating_cnt = int(float(row.get("ratingCount"))) if pd.notna(row.get("ratingCount")) else 0
    avg_rating = round(float(row.get("avg_rating")), 2) if pd.notna(row.get("avg_rating")) else 4.2

    # Parse attributes dictionary string
    attr_str = str(row.get("p_attributes", ""))
    attr_dict = {}
    try:
        if attr_str.startswith("{"):
            attr_dict = ast.literal_eval(attr_str)
    except Exception:
        pass

    occasion = attr_dict.get("Occasion", "")
    fabric = attr_dict.get("Top Fabric", "") or attr_dict.get("Bottom Fabric", "")
    pattern = attr_dict.get("Print or Pattern Type", "")

    full_text = f"{name} {brand} {colour} {raw_desc} {occasion} {fabric} {pattern}"
    tags = infer_tags(full_text)
    if colour and colour.lower() not in [t.lower() for t in tags]:
        tags.append(colour.lower())
    if occasion and occasion.lower() not in [t.lower() for t in tags]:
        tags.append(occasion.lower())

    category = make_category(tags)
    vibe_vec = get_vibe_vector(tags, category_str=category)
    vibe_list = vibe_vec.tolist() if hasattr(vibe_vec, 'tolist') else list(vibe_vec)

    product_item = {
        "id": current_id,
        "p_id": p_id,
        "name": name,
        "description": raw_desc[:300] if raw_desc else name,
        "category": category,
        "price": price,
        "colour": colour,
        "brand": brand,
        "image_url": img_url,
        "product_url": f"https://www.myntra.com/{p_id}",
        "ratingCount": rating_cnt,
        "avg_rating": avg_rating,
        "tags": tags,
        "zip_codes": [],
        "embedding": vibe_list
    }

    new_products.append(product_item)
    existing_ids.add(current_id)
    if current_id >= next_id:
        next_id = current_id + 1

print(f"Processed {len(new_products)} new products from dataset.")

final_catalog = existing_catalog + new_products
print(f"Total catalog count after integration: {len(final_catalog)}")

with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(final_catalog, f, indent=2)

print(f"Saved updated catalog to {LOCAL_CATALOG_FILE}")

# Sync to frontend catalog_fallback.js
js_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(final_catalog, indent=2) + ";\n"
with open(js_file, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Synced catalog to {js_file}")
