import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from scoring_engine import cosine_similarity, normalize_cosine_score
from main import get_vibe_vector, FALLBACK_CREATORS, FALLBACK_STORES

with open('scratch/full_269_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Take exact top 269 items if total > 269
catalog_269 = catalog[:269]
print(f"Total catalog evaluated: {len(catalog_269)} products")

target_vibe = "casual streetwear boots leather fashion"
ref_text_vec = get_vibe_vector(target_vibe)

patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_stores = FALLBACK_STORES.get("800008", [])
patna_vecs = [c['vector'] for c in patna_creators] + [s['vector'] for s in patna_stores]
patna_ref_vec = np.mean(patna_vecs, axis=0).tolist()

hybrid_results = []

for p in catalog_269:
    pid = p.get("id")
    pname = p.get("name", "")
    pcat = p.get("category", "")
    pprice = p.get("price", 1499.0)
    
    tags_raw = p.get("tags", [])
    if isinstance(tags_raw, list):
        ptags = [str(t).lower() for t in tags_raw]
    else:
        ptags = [str(tags_raw).lower()]
        
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    if img_vec:
        cos_vis = cosine_similarity(patna_ref_vec, img_vec)
        s_vis = normalize_cosine_score(cos_vis)
        cos_text = cosine_similarity(ref_text_vec, img_vec)
        s_text = normalize_cosine_score(cos_text)
    else:
        s_vis = 0.5
        s_text = 0.5

    match_tags = [t for t in ptags if any(k in t for k in ["boot", "leather", "casual", "streetwear", "footwear", "ankle"])]
    s_tag = min(1.0, len(match_tags) / 3.0)

    # Hybrid Score = (0.5 * Visual) + (0.3 * Text) + (0.2 * Tag)
    s_hybrid = (0.5 * s_vis) + (0.3 * s_text) + (0.2 * s_tag)
    hybrid_match_pct = round(s_hybrid * 100, 2)

    hybrid_results.append({
        "id": pid,
        "name": pname,
        "category": pcat,
        "price": pprice,
        "tags": ptags,
        "s_vis": round(s_vis, 4),
        "s_text": round(s_text, 4),
        "s_tag": round(s_tag, 4),
        "s_hybrid": round(s_hybrid, 4),
        "hybrid_match_pct": hybrid_match_pct,
        "product_link": p.get("product_url") or p.get("myntra_url") or p.get("url") or f"https://www.myntra.com/{pid}"
    })

# Rank descending by Hybrid Match Percentage
hybrid_results.sort(key=lambda x: x["hybrid_match_pct"], reverse=True)

# Find ALL boots/footwear items in 269 catalog
all_boots = []
for rank, item in enumerate(hybrid_results, 1):
    name_lower = item["name"].lower()
    cat_lower = item["category"].lower()
    tags_lower = item["tags"]
    
    if "boot" in name_lower or "boot" in cat_lower or any("boot" in t for t in tags_lower):
        item_copy = item.copy()
        item_copy["rank"] = rank
        all_boots.append(item_copy)

print(f"\nFound {len(all_boots)} boots items in full 269 catalog ranking:")
for b in all_boots:
    print(f"Rank #{b['rank']} out of 269 | ID {b['id']} | {b['name']} | Hybrid Match: {b['hybrid_match_pct']}% | Price: Rs.{b['price']}")

with open('scratch/boots_269_full_ranking.json', 'w', encoding='utf-8') as f:
    json.dump({
        "total_catalog_size": len(catalog_269),
        "boots_count": len(all_boots),
        "boots_list": all_boots
    }, f, indent=2)

print("\nSaved boots full 269 ranking to scratch/boots_269_full_ranking.json")
