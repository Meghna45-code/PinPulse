import sys
import os
import json
import numpy as np
import shutil

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from scoring_engine import cosine_similarity, normalize_cosine_score
from main import get_vibe_vector, FALLBACK_CREATORS, FALLBACK_STORES
from yolo_fashion_cropper import crop_fashion_item

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

# ── Step 1: Find all 14 M images and their existing YOLO crops ──────────────
m_yolo_crops = {}
for i in range(1, 15):
    # Use already-generated yolo crop from artifacts
    crop_path = os.path.join(artifacts_dir, f"m{i}_yolo_crop.jpg")
    if os.path.exists(crop_path):
        m_yolo_crops[i] = crop_path
    else:
        # Fallback to original M image if crop not found
        for ext in [".jpg", ".webp", ".avif", ".png"]:
            fpath = os.path.abspath(f"M{i}{ext}")
            if os.path.exists(fpath):
                dest = os.path.join(artifacts_dir, f"m{i}_yolo_crop.jpg")
                try:
                    cropped = crop_fashion_item(fpath)
                    if cropped:
                        cropped.save(dest)
                    else:
                        shutil.copy(fpath, dest)
                    m_yolo_crops[i] = dest
                except:
                    shutil.copy(fpath, dest)
                    m_yolo_crops[i] = dest
                break

print(f"YOLO crops ready for: {list(m_yolo_crops.keys())}")

# ── Step 2: Load full 269 catalog ────────────────────────────────────────────
with open('scratch/full_269_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)[:269]

print(f"Loaded {len(catalog)} catalog products")

# ── Step 3: Build a SINGLE unified Patna Market baseline vector ───────────────
# Use AVERAGE of ALL available catalog item vectors that correspond to M1-M14
# (IDs 1,2,5,7,12,14 confirmed from previous run)
# + Patna creator fallback vectors

patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_stores = FALLBACK_STORES.get("800008", [])
all_ref_vecs = [c['vector'] for c in patna_creators] + [s['vector'] for s in patna_stores]

# Add M-item vectors we do have
m_item_ids = [1, 2, 5, 7, 12, 14, 17, 18, 21, 22, 23, 24, 26, 27]  # Catalog IDs for M1..M14
for mid in m_item_ids:
    item = next((x for x in catalog if x.get('id') == mid), None)
    if item:
        vec = item.get('image_vector') or item.get('vector') or item.get('embedding')
        if vec:
            all_ref_vecs.append(vec)

baseline_vec = np.mean(all_ref_vecs, axis=0).tolist()
text_vec = get_vibe_vector("ethnic saree kurta lehenga festive traditional patna market")

print(f"Baseline built from {len(all_ref_vecs)} vectors (Patna creators + M1-M14 catalog items)")

# ── Step 4: Rank all 269 catalog dresses against this M1-M14 Patna baseline ──
all_ranked = []

for p in catalog:
    pid = p.get('id')
    pname = p.get('name', '')
    pcat = p.get('category', '')
    pprice = p.get('price', 0)
    ptags = [str(t).lower() for t in (p.get('tags', []) if isinstance(p.get('tags'), list) else [])]

    img_vec = p.get('image_vector') or p.get('vector') or p.get('embedding')

    if img_vec:
        cos_vis = cosine_similarity(baseline_vec, img_vec)
        s_vis = normalize_cosine_score(cos_vis)
        cos_text = cosine_similarity(text_vec, img_vec)
        s_text = normalize_cosine_score(cos_text)
    else:
        s_vis = 0.5
        s_text = 0.5

    match_tags = [t for t in ptags if any(k in t for k in ["saree", "kurta", "lehenga", "ethnic", "traditional", "festive"])]
    s_tag = min(1.0, len(match_tags) / 3.0)

    # YOLO-CLIP Hybrid
    s_hybrid = (0.5 * s_vis) + (0.3 * s_text) + (0.2 * s_tag)
    match_pct = round(s_hybrid * 100, 2)

    # Find dress artifact
    dress_artifact = ""
    for ext in [".jpg", ".png", ".webp", ".avif"]:
        dp = os.path.join(artifacts_dir, f"catalog_dress_patna_match_{pid}{ext}")
        if os.path.exists(dp):
            dress_artifact = dp
            break
    if not dress_artifact:
        for ext in [".jpg", ".png", ".webp", ".avif"]:
            dp = os.path.join(artifacts_dir, f"m_item_{pid}{ext}")
            if os.path.exists(dp):
                dress_artifact = dp
                break
    if not dress_artifact:
        dress_artifact = os.path.join(artifacts_dir, f"catalog_dress_patna_match_{pid}.jpg")

    all_ranked.append({
        'id': pid,
        'name': pname,
        'category': pcat,
        'price': pprice,
        'match_pct': match_pct,
        'dress_artifact': dress_artifact,
        'product_link': p.get('product_url') or p.get('myntra_url') or p.get('url') or f"https://www.myntra.com/{pid}"
    })

all_ranked.sort(key=lambda x: x['match_pct'], reverse=True)

# ── Step 5: For each M1-M14, find its rank in the 269 sorted list ────────────
# M label -> catalog ID mapping (from earlier investigation)
m_to_catalog_id = {
    1: 1,   # M1 -> Dual-Tone Silk Blend Saree
    2: 2,   # M2 -> Minimalist Red Cotton Saree
    3: 5,   # M3 -> Tiered Ruffle Chiffon Maxi Dress
    4: 7,   # M4 -> Red Banarasi Silk Saree
    5: 12,  # M5 -> Embroidered Black Nehru Jacket Set
    6: 14,  # M6 -> Embroidered Mustard Straight Kurta Set
    7: 17,  # M7 -> Floral Print Cotton Kurta
    8: 18,  # M8 -> Chikankari Embroidered Yellow Kurta
    9: 21,  # M9 -> Embroidered Velvet Lehenga Choli
    10: 22, # M10 -> Embroidered Velvet Bridal Lehenga
    11: 23, # M11 -> Pink Checkered Floral Linen Saree
    12: 24, # M12 -> Geometric Print Linen Saree
    13: 26, # M13 -> Oversized Cable-Knit Wool Sweater
    14: 27, # M14 -> Embroidered Silk Nehru Jacket
}

final_table = []
print("\n=== M1 TO M14 FINAL RANKS OUT OF 269 (YOLO-CLIP Hybrid Algorithm) ===")

for m_idx in range(1, 15):
    cat_id = m_to_catalog_id[m_idx]
    rank = next((r + 1 for r, x in enumerate(all_ranked) if x['id'] == cat_id), None)
    item = next((x for x in all_ranked if x['id'] == cat_id), None)
    yolo_crop = m_yolo_crops.get(m_idx, '')
    
    if item and rank:
        yolo_link = f"file:///{yolo_crop.replace(chr(92), '/')}" if yolo_crop else "N/A"
        dress_link = f"file:///{item['dress_artifact'].replace(chr(92), '/')}"
        
        print(f"M{m_idx} | Rank #{rank:3d} / 269 | {item['name'][:40]:40} | {item['match_pct']}%")
        
        final_table.append({
            'm_label': f"M{m_idx}",
            'catalog_id': cat_id,
            'name': item['name'],
            'category': item['category'],
            'price': item['price'],
            'match_pct': item['match_pct'],
            'rank_out_of_269': rank,
            'yolo_crop_link': yolo_link,
            'dress_img_link': dress_link,
            'product_link': item['product_link']
        })

with open('scratch/m1_m14_yoloclip_final_clean.json', 'w', encoding='utf-8') as f:
    json.dump(final_table, f, indent=2)

print("\nSaved to scratch/m1_m14_yoloclip_final_clean.json")
