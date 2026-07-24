import sys
import json
import os
import glob
import pandas as pd

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from main import get_vibe_vector

print("=== Merging all products to build the exact 269 Catalog Dataset ===")

all_products = []
seen_ids = set()
seen_urls = set()

# 1. Add local_catalog.json
with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    lc = json.load(f)
    for p in lc:
        pid = p.get('id')
        purl = p.get('product_url') or p.get('myntra_url') or p.get('url')
        seen_ids.add(str(pid))
        if purl:
            seen_urls.add(purl)
        all_products.append(p)

print(f"Loaded {len(all_products)} products from local_catalog.json")

# 2. Add dev_scripts/large_catalog_checkpoint.json
if os.path.exists('backend/dev_scripts/large_catalog_checkpoint.json'):
    with open('backend/dev_scripts/large_catalog_checkpoint.json', 'r', encoding='utf-8') as f:
        lcc = json.load(f)
    added_lcc = 0
    for p in lcc:
        pid = p.get('id')
        purl = p.get('product_url') or p.get('myntra_url') or p.get('url')
        if str(pid) not in seen_ids and (not purl or purl not in seen_urls):
            seen_ids.add(str(pid))
            if purl:
                seen_urls.add(purl)
            all_products.append(p)
            added_lcc += 1
    print(f"Added {added_lcc} new products from large_catalog_checkpoint.json")

# 3. Add products from Fashion Apparel.xlsx and Fashion Apparel2.xlsx
next_id = max([int(x) for x in seen_ids if x.isdigit()] or [300]) + 1

for xlsx in ["excel_sheets/Fashion Apparel.xlsx", "excel_sheets/Fashion Apparel2.xlsx"]:
    if os.path.exists(xlsx):
        df = pd.read_excel(xlsx)
        added_excel = 0
        for idx, row in df.iterrows():
            row_vals = [str(v) for v in row.values if pd.notna(v)]
            url = next((v for v in row_vals if 'myntra.com' in v or 'http' in v), None)
            desc = next((v for v in row_vals if 'myntra.com' not in v and not v.isdigit()), f"Fashion Dress Item {next_id}")
            
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
                
            # Create synthetic product entry with 512-D vector
            p_entry = {
                "id": next_id,
                "name": desc[:60],
                "category": "ethnic" if any(k in desc.lower() for k in ["saree", "kurta", "lehenga", "dhoti"]) else "casual",
                "price": 1499.0,
                "tags": [t for t in desc.lower().split() if len(t) > 3],
                "product_url": url or f"https://www.myntra.com/{next_id}",
                "embedding": get_vibe_vector(desc),
                "image_vector": get_vibe_vector(desc)
            }
            all_products.append(p_entry)
            next_id += 1
            added_excel += 1
        print(f"Added {added_excel} products from {xlsx}")

print(f"\nTOTAL EXPANDED CATALOG COUNT: {len(all_products)} products")

with open('scratch/full_269_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, indent=2)

print("Saved full catalog to scratch/full_269_catalog.json")
