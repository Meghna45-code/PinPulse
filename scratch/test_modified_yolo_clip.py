import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from scoring_engine import cosine_similarity, normalize_cosine_score
from main import get_vibe_vector

with open('scratch/full_269_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)[:269]

print(f"Total catalog evaluated: {len(catalog)} products")

# Category Compatibility Matrix C(Target, Product)
CATEGORY_COMPATIBILITY = {
    ("ethnic", "ethnic"): 1.0,
    ("ethnic", "casual"): 0.8,
    ("ethnic", "western"): 0.7,
    ("ethnic", "festive"): 1.0,
    ("ethnic", "winter"): 0.6,
    ("ethnic", "footwear"): 0.15,      # Heavy slash for footwear when searching dress/apparel
    ("ethnic", "accessories"): 0.20,   # Heavy slash for jewelry/bags
    ("casual", "footwear"): 0.25,
    ("casual", "accessories"): 0.30,
}

def get_category_compat(target_cat, product_cat):
    t = target_cat.lower()
    p = product_cat.lower()
    if t == p:
        return 1.0
    if (t, p) in CATEGORY_COMPATIBILITY:
        return CATEGORY_COMPATIBILITY[(t, p)]
    if "footwear" in p or "shoe" in p or "boot" in p:
        return 0.15 if "footwear" not in t else 1.0
    if "accessories" in p or "jewelry" in p or "ring" in p:
        return 0.20 if "accessories" not in t else 1.0
    return 0.75

target_category = "ethnic" # Searching for ethnic dresses/sarees/kurtas
target_vibe = "ethnic saree kurta festive traditional"
target_text_vec = get_vibe_vector(target_vibe)

# Patna Creator visual reference vector
from main import FALLBACK_CREATORS
patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_vecs = [c['vector'] for c in patna_creators]
patna_ref_vec = np.mean(patna_vecs, axis=0).tolist()

modified_results = []

for p in catalog:
    pid = p.get("id")
    pname = p.get("name", "")
    pcat = p.get("category", "")
    pprice = p.get("price", 1499.0)
    ptags = [str(t).lower() for t in (p.get("tags", []) if isinstance(p.get("tags"), list) else [p.get("tags")])]
    
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    
    # 1. Visual CLIP Score
    cos_vis = cosine_similarity(patna_ref_vec, img_vec) if img_vec else 0.0
    s_vis = normalize_cosine_score(cos_vis)
    
    # 2. Text CLIP Score
    cos_text = cosine_similarity(target_text_vec, img_vec) if img_vec else 0.0
    s_text = normalize_cosine_score(cos_text)
    
    # 3. Category Gated Tag Score (Only apply tag boost if category is compatible)
    cat_compat = get_category_compat(target_category, pcat)
    
    match_tags = [t for t in ptags if any(k in t for k in ["saree", "kurta", "lehenga", "ethnic", "traditional"])]
    s_tag_raw = min(1.0, len(match_tags) / 3.0)
    s_tag = s_tag_raw * cat_compat
    
    # 4. Modified Hybrid Score with Category Gate Multiplier
    s_hybrid_raw = (0.5 * s_vis) + (0.3 * s_text) + (0.2 * s_tag)
    
    # Apply Category Compatibility Gate
    s_hybrid_gated = s_hybrid_raw * cat_compat
    gated_match_pct = round(s_hybrid_gated * 100, 2)
    
    modified_results.append({
        "id": pid,
        "name": pname,
        "category": pcat,
        "price": pprice,
        "raw_pct": round(s_hybrid_raw * 100, 2),
        "gated_pct": gated_match_pct,
        "cat_compat": cat_compat,
        "tags": ptags
    })

modified_results.sort(key=lambda x: x["gated_pct"], reverse=True)

# Find boots rank in MODIFIED system
boots_modified = []
for rank, item in enumerate(modified_results, 1):
    n_lower = item["name"].lower()
    c_lower = item["category"].lower()
    t_lower = item["tags"]
    if "boot" in n_lower or "boot" in c_lower or any("boot" in t for t in t_lower):
        item_copy = item.copy()
        item_copy["new_rank"] = rank
        boots_modified.append(item_copy)

print(f"\n=== MODIFIED ALGORITHM RESULTS FOR BOOTS IN 269 CATALOG ===")
for b in boots_modified:
    print(f"Item ID {b['id']}: {b['name']}")
    print(f"  Old Un-gated Match: {b['raw_pct']}% | New Category-Gated Match: {b['gated_pct']}%")
    print(f"  Category Compat Multiplier: {b['cat_compat']}x")
    print(f"  NEW RANK IN 269 CATALOG: Rank #{b['new_rank']} out of 269 (Sunk down from Rank #1!)")

print("\n=== TOP 5 ITEMS IN MODIFIED ALGORITHM (Dresses & Apparel Only) ===")
for r, item in enumerate(modified_results[:5], 1):
    print(f"Rank #{r}: ID {item['id']} | {item['name']} | Cat: {item['category']} | Gated Match: {item['gated_pct']}%")
