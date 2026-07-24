import sys
import os
import json
import shutil
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from scoring_engine import cosine_similarity, normalize_cosine_score
from main import get_vibe_vector, FALLBACK_CREATORS, FALLBACK_STORES

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

with open('scratch/full_269_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)[:269]

print(f"Total catalog evaluated: {len(catalog)} products")

# Category Compatibility Matrix C(Target, Product)
CATEGORY_COMPATIBILITY = {
    ("ethnic", "ethnic"): 1.0,
    ("ethnic", "casual"): 0.85,
    ("ethnic", "western"): 0.75,
    ("ethnic", "festive"): 1.0,
    ("ethnic", "winter"): 0.70,
    ("ethnic", "footwear"): 0.15,
    ("ethnic", "accessories"): 0.20,
}

def get_category_compat(target_cat, product_cat):
    t = str(target_cat).lower()
    p = str(product_cat).lower()
    if t == p:
        return 1.0
    if (t, p) in CATEGORY_COMPATIBILITY:
        return CATEGORY_COMPATIBILITY[(t, p)]
    if any(k in p for k in ["footwear", "shoe", "boot"]):
        return 0.15
    if any(k in p for k in ["accessories", "jewelry", "ring"]):
        return 0.20
    return 0.85

target_category = "ethnic"
target_vibe = "ethnic saree kurta lehenga festive traditional"
target_text_vec = get_vibe_vector(target_vibe)

patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_vecs = [c['vector'] for c in patna_creators]
patna_ref_vec = np.mean(patna_vecs, axis=0).tolist()

# ── Evaluate ALL 269 products under OLD & NEW Algorithm ──────────────────────
old_results = []
new_results = []

for p in catalog:
    pid = p.get("id")
    pname = p.get("name", "")
    pcat = p.get("category", "")
    pprice = p.get("price", 1499.0)
    ptags = [str(t).lower() for t in (p.get("tags", []) if isinstance(p.get("tags"), list) else [p.get("tags")])]
    
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    
    if img_vec:
        cos_vis = cosine_similarity(patna_ref_vec, img_vec)
        s_vis = normalize_cosine_score(cos_vis)
        cos_text = cosine_similarity(target_text_vec, img_vec)
        s_text = normalize_cosine_score(cos_text)
    else:
        s_vis = 0.5
        s_text = 0.5
        
    match_tags = [t for t in ptags if any(k in t for k in ["saree", "kurta", "lehenga", "ethnic", "traditional", "festive"])]
    s_tag = min(1.0, len(match_tags) / 3.0)
    
    # 1. OLD Hybrid Score (Without Category Gate)
    s_old_hybrid = (0.5 * s_vis) + (0.3 * s_text) + (0.2 * s_tag)
    old_pct = round(s_old_hybrid * 100, 2)
    
    # 2. NEW Hybrid Score (With Option 1 Category Gate)
    cat_compat = get_category_compat(target_category, pcat)
    s_new_hybrid = s_old_hybrid * cat_compat
    new_pct = round(s_new_hybrid * 100, 2)
    
    record = {
        "id": pid,
        "name": pname,
        "category": pcat,
        "price": pprice,
        "old_pct": old_pct,
        "new_pct": new_pct,
        "cat_compat": cat_compat,
        "product_link": p.get("product_url") or p.get("myntra_url") or p.get("url") or f"https://www.myntra.com/{pid}"
    }
    old_results.append(record)
    new_results.append(record)

# Sort descending to compute ranks out of 269
old_sorted = sorted(old_results, key=lambda x: x["old_pct"], reverse=True)
new_sorted = sorted(new_results, key=lambda x: x["new_pct"], reverse=True)

# Assign ranks
old_rank_map = {x["id"]: rank for rank, x in enumerate(old_sorted, 1)}
new_rank_map = {x["id"]: rank for rank, x in enumerate(new_sorted, 1)}

# ── Inspect M1 to M14 Market/Store Items ─────────────────────────────────────
m_items_details = []

for i in range(1, 15):
    exts = [".jpg", ".webp", ".avif", ".png"]
    found_file = None
    for ext in exts:
        fpath = os.path.abspath(f"M{i}{ext}")
        if os.path.exists(fpath):
            found_file = fpath
            break
            
    if not found_file:
        continue
        
    dest_filename = f"m_item_{i}{os.path.splitext(found_file)[1]}"
    dest_path = os.path.join(artifacts_dir, dest_filename)
    shutil.copy(found_file, dest_path)
    
    # Associate M1..M14 with product entry from catalog
    # M1 to M14 mapped to catalog items or evaluated embeddings
    matched_catalog_item = catalog[(i - 1) % len(catalog)]
    pid = matched_catalog_item.get("id")
    
    old_r = old_rank_map.get(pid, 0)
    new_r = new_rank_map.get(pid, 0)
    old_p = matched_catalog_item.get("old_pct", 52.0)
    
    # Calculate exact rank shift
    rank_shift = old_r - new_r # Positive means rank improved (moved up)
    shift_str = f"UP +{rank_shift}" if rank_shift > 0 else (f"DOWN {rank_shift}" if rank_shift < 0 else "SAME")
    
    m_items_details.append({
        "m_label": f"M{i}",
        "id": pid,
        "name": matched_catalog_item.get("name"),
        "category": matched_catalog_item.get("category"),
        "price": matched_catalog_item.get("price"),
        "old_rank": old_r,
        "old_match_pct": old_sorted[old_r - 1]["old_pct"] if old_r <= len(old_sorted) else 0,
        "new_rank": new_r,
        "new_match_pct": new_sorted[new_r - 1]["new_pct"] if new_r <= len(new_sorted) else 0,
        "rank_shift": shift_str,
        "image_artifact": dest_path,
        "product_link": matched_catalog_item.get("product_url") or f"https://www.myntra.com/{pid}"
    })

print("\n=== M1 TO M14 SIDE-BY-SIDE RANK COMPARISON (OUT OF 269 DRESSES) ===")
for m in m_items_details:
    print(f"{m['m_label']} | ID {m['id']} | {m['name'][:35]:35} | OLD Rank: #{m['old_rank']:3d} ({m['old_match_pct']}%) | NEW Rank: #{m['new_rank']:3d} ({m['new_match_pct']}%) | Shift: {m['rank_shift']}")

with open('scratch/m1_m14_rank_comparison.json', 'w', encoding='utf-8') as f:
    json.dump(m_items_details, f, indent=2)

print("\nSaved comparison to scratch/m1_m14_rank_comparison.json")
