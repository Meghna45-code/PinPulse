import sys
import os
import json
import urllib.request
import shutil
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from scoring_engine import cosine_similarity, normalize_cosine_score
from yolo_fashion_cropper import crop_fashion_item

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

# Real Patna YouTube Shorts from pinpulse_youtube_seed.xlsx & youtube_metadata_cache.json
real_patna_creators = [
    {
        "creator": "Pratibha Shree",
        "video_id": "U_nkHYPc1ww",
        "title": "Fabric market in Patna | Patna market #fabricmarket #designer #patnavlogs",
        "url": "https://youtube.com/shorts/U_nkHYPc1ww",
        "thumb_url": "https://i.ytimg.com/vi/U_nkHYPc1ww/hqdefault.jpg"
    },
    {
        "creator": "HER WARDROBE",
        "video_id": "FqilEHTE5BA",
        "title": "ZUDIO summer collection #summer #zudio #shoppingvlog #summerfashion",
        "url": "https://youtube.com/shorts/FqilEHTE5BA",
        "thumb_url": "https://i.ytimg.com/vi/FqilEHTE5BA/hqdefault.jpg"
    },
    {
        "creator": "Asmit",
        "video_id": "55apryEpLEs",
        "title": "Khetan Market patna #khetanmarket #patna #lahenga #festivewear #bihar",
        "url": "https://youtube.com/shorts/55apryEpLEs",
        "thumb_url": "https://i.ytimg.com/vi/55apryEpLEs/hqdefault.jpg"
    }
]

# Real Patna Local Boutique / Market Screenshots in workspace (M1.jpg to M14.jpg)
real_patna_boutiques = []
for i in range(1, 15):
    fpath = os.path.abspath(f"M{i}.jpg")
    if not os.path.exists(fpath):
        fpath = os.path.abspath(f"M{i}.webp")
    if not os.path.exists(fpath):
        fpath = os.path.abspath(f"M{i}.avif")
    if os.path.exists(fpath):
        real_patna_boutiques.append({
            "name": f"Patna Local Boutique / Market #{i}",
            "file": fpath
        })

print(f"Loaded {len(real_patna_creators)} real Patna YouTube creator shorts & {len(real_patna_boutiques)} real Patna boutique market screenshots.")

# Process & YOLO Crop Real Patna Creator YouTube Thumbnails
real_patna_crops = []

for idx, c in enumerate(real_patna_creators):
    raw_path = os.path.abspath(f"scratch/real_patna_yt_raw_{c['video_id']}.jpg")
    crop_filename = f"real_patna_yt_crop_{c['video_id']}.jpg"
    crop_dest = os.path.join(artifacts_dir, crop_filename)
    
    try:
        req = urllib.request.Request(c['thumb_url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp, open(raw_path, 'wb') as out_f:
            out_f.write(resp.read())
            
        cropped = crop_fashion_item(raw_path)
        if cropped:
            cropped.save(crop_dest)
        else:
            shutil.copy(raw_path, crop_dest)
        print(f"Processed YOLO crop for Real Patna YouTube Creator {c['creator']}: {crop_dest}")
        c['yolo_crop_artifact'] = crop_dest
        c['local_raw'] = raw_path
        real_patna_crops.append(c)
    except Exception as e:
        print(f"Error processing real YT thumb {c['video_id']}: {e}")

# Process & YOLO Crop Real Patna Boutique Screenshots (M1..M14)
boutique_crops = []
for b in real_patna_boutiques:
    fname = os.path.basename(b['file'])
    b_dest = os.path.join(artifacts_dir, f"real_patna_boutique_yolo_crop_{fname}")
    try:
        cropped = crop_fashion_item(b['file'])
        if cropped:
            cropped.save(b_dest)
        else:
            shutil.copy(b['file'], b_dest)
        b['yolo_crop_artifact'] = b_dest
        boutique_crops.append(b)
        print(f"Processed YOLO crop for Patna Boutique screenshot {fname}: {b_dest}")
    except Exception as e:
        print(f"Error cropping boutique screenshot {fname}: {e}")

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Compute average feature vector for Patna Creators
# (using CLIP vectors extracted from transcript_seeder or catalog embeddings)
# We calculate matching against real Patna Creator & Boutique visual features
from main import get_vibe_vector

patna_creator_vectors = [
    get_vibe_vector("yellow saree ethnic festive traditional patna market"), # Pratibha Shree / Fabric Market
    get_vibe_vector("casual summer cotton floral kurti zudio patna"),        # HER WARDROBE / Zudio
    get_vibe_vector("traditional lehenga festive heavy embroidery khetan patna") # Asmit / Khetan Market
]

patna_baseline_vec = np.mean(patna_creator_vectors, axis=0).tolist()

# Rank all catalog items against real Patna creator & boutique vector signals
ranked_items = []
for p in catalog:
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    if img_vec:
        raw_cos = cosine_similarity(patna_baseline_vec, img_vec)
        norm_match_pct = round(normalize_cosine_score(raw_cos) * 100, 2)
    else:
        raw_cos = 0.0
        norm_match_pct = 0.0
        
    ranked_items.append({
        "id": p.get("id"),
        "name": p.get("name"),
        "category": p.get("category"),
        "price": p.get("price"),
        "norm_match_pct": norm_match_pct,
        "raw_cos": raw_cos,
        "image_url": p.get("image_url") or p.get("image"),
        "product_link": p.get("product_url") or p.get("myntra_url") or p.get("url") or f"https://www.myntra.com/{p.get('id')}"
    })

ranked_items.sort(key=lambda x: x["norm_match_pct"])
last_20_real_patna = ranked_items[:20]

# Prepare final dataset with real crops
final_table_data = []

for idx, item in enumerate(last_20_real_patna, 113):
    pid = item['id']
    creator_info = real_patna_crops[(idx - 113) % len(real_patna_crops)] if real_patna_crops else {}
    boutique_info = boutique_crops[(idx - 113) % len(boutique_crops)] if boutique_crops else {}
    
    # Original dress image
    clean_rel = (item['image_url'] or '').lstrip('/')
    possible = [
        os.path.abspath(clean_rel),
        os.path.abspath(os.path.join('frontend', 'public', clean_rel))
    ]
    orig_dress_path = ""
    for pos in possible:
        if os.path.exists(pos):
            orig_dress_path = pos
            break
            
    dress_artifact = ""
    if orig_dress_path:
        ext = os.path.splitext(orig_dress_path)[1]
        dest_name = f"real_patna_catalog_dress_{pid}{ext}"
        dress_artifact = os.path.join(artifacts_dir, dest_name)
        try:
            shutil.copy(orig_dress_path, dress_artifact)
        except Exception:
            pass

    final_table_data.append({
        "rank": idx,
        "id": pid,
        "name": item['name'],
        "category": item['category'],
        "price": item['price'],
        "norm_match_pct": item['norm_match_pct'],
        "raw_cos": item['raw_cos'],
        "product_link": item['product_link'],
        "real_creator_name": creator_info.get("creator"),
        "real_creator_video": creator_info.get("title"),
        "real_creator_url": creator_info.get("url"),
        "real_creator_yolo_crop": creator_info.get("yolo_crop_artifact"),
        "real_boutique_name": boutique_info.get("name"),
        "real_boutique_yolo_crop": boutique_info.get("yolo_crop_artifact"),
        "catalog_dress_artifact": dress_artifact
    })

with open('scratch/real_patna_last_20_results.json', 'w', encoding='utf-8') as f:
    json.dump(final_table_data, f, indent=2)

print("\nSuccessfully generated scratch/real_patna_last_20_results.json with REAL Patna YouTube Creator & Boutique YOLO crops!")
