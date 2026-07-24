import sys
import os
import json
import urllib.request
import numpy as np

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from main import FALLBACK_CREATORS, FALLBACK_STORES
from scoring_engine import cosine_similarity, normalize_cosine_score
from yolo_fashion_cropper import crop_fashion_item

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Get Patna creators and stores
patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_stores = FALLBACK_STORES.get("800008", [])

# Combine Patna creator and store vectors to form the Patna Trend Target Vector
patna_vectors = []
patna_thumbnails = []

for c in patna_creators:
    patna_vectors.append(c['vector'])
    for v in c.get('videos', []):
        if v.get('video_screenshot_url'):
            patna_thumbnails.append({
                "creator": c.get('name'),
                "title": v.get('title'),
                "url": v.get('video_screenshot_url')
            })

for s in patna_stores:
    patna_vectors.append(s['vector'])

# Average vector for Patna regional trend baseline
patna_trend_vector = np.mean(patna_vectors, axis=0).tolist()

print(f"Computed Patna baseline vector across {len(patna_vectors)} creator/store signals.")

# Rank all catalog products against Patna creator & boutique baseline vector
patna_ranked = []
for p in catalog:
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    if img_vec:
        raw_cos = cosine_similarity(patna_trend_vector, img_vec)
        norm_match_pct = round(normalize_cosine_score(raw_cos) * 100, 2)
    else:
        raw_cos = 0.0
        norm_match_pct = 0.0
        
    patna_ranked.append({
        "id": p.get("id"),
        "name": p.get("name"),
        "category": p.get("category"),
        "price": p.get("price"),
        "raw_cos": raw_cos,
        "norm_match_pct": norm_match_pct,
        "image_url": p.get("image_url") or p.get("image"),
        "product_link": p.get("product_url") or p.get("myntra_url") or p.get("url") or f"https://www.myntra.com/{p.get('id')}"
    })

# Sort ascending to get lowest matching items against Patna trend baseline
patna_ranked.sort(key=lambda x: x["norm_match_pct"])
last_20_patna = patna_ranked[:20] # 20 lowest matches against Patna

print("\n=== LAST 20 LOWEST MATCHES AGAINST PATNA CREATOR & BOUTIQUE THUMBNAILS ===")
for idx, item in enumerate(last_20_patna, 113):
    print(f"Rank {idx:3d} | ID {item['id']:3} | {item['name'][:40]:40} | Match: {item['norm_match_pct']}% | Cos: {item['raw_cos']:.4f}")

# Download and YOLO crop Patna Creator video thumbnails
patna_yt_crops = []
for i, thumb in enumerate(patna_thumbnails):
    raw_path = os.path.abspath(f"scratch/patna_yt_raw_{i}.jpg")
    crop_path = os.path.join(artifacts_dir, f"yolo_crop_patna_yt_thumb_{i}.jpg")
    try:
        req = urllib.request.Request(thumb['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp, open(raw_path, 'wb') as out_f:
            out_f.write(resp.read())
        cropped = crop_fashion_item(raw_path)
        if cropped:
            cropped.save(crop_path)
        print(f"Saved YOLO cropped Patna YT thumbnail #{i}: {crop_path}")
        patna_yt_crops.append(crop_path)
    except Exception as e:
        print(f"Error processing Patna thumbnail #{i}: {e}")

# Save results
out_data = []
for idx, item in enumerate(last_20_patna, 113):
    pid = item['id']
    # Patna thumbnail assigned to item
    assigned_patna_crop = patna_yt_crops[(idx - 113) % len(patna_yt_crops)] if patna_yt_crops else ""
    assigned_yt_info = patna_thumbnails[(idx - 113) % len(patna_thumbnails)] if patna_thumbnails else {}
    
    # Original dress image
    clean_rel = (item['image_url'] or '').lstrip('/')
    possible = [
        os.path.abspath(clean_rel),
        os.path.abspath(os.path.join('frontend', 'public', clean_rel))
    ]
    orig_dress = ""
    for pos in possible:
        if os.path.exists(pos):
            orig_dress = pos
            break
            
    dress_artifact_path = ""
    if orig_dress:
        ext = os.path.splitext(orig_dress)[1]
        dest_name = f"catalog_dress_patna_match_{pid}{ext}"
        dress_artifact_path = os.path.join(artifacts_dir, dest_name)
        shutil_copy = True
        try:
            import shutil
            shutil.copy(orig_dress, dress_artifact_path)
        except Exception:
            pass

    out_data.append({
        "rank": idx,
        "id": pid,
        "name": item['name'],
        "category": item['category'],
        "price": item['price'],
        "norm_match_pct": item['norm_match_pct'],
        "raw_cos": item['raw_cos'],
        "product_link": item['product_link'],
        "patna_creator_name": assigned_yt_info.get("creator", "Patna Creator Trend Feed"),
        "patna_video_title": assigned_yt_info.get("title", "Patna Regional Fashion Review"),
        "patna_yt_yolo_crop_artifact": assigned_patna_crop,
        "catalog_dress_artifact": dress_artifact_path
    })

with open('scratch/patna_last_20_results.json', 'w', encoding='utf-8') as f:
    json.dump(out_data, f, indent=2)

print(f"\nSaved all {len(out_data)} Patna-ranked items to scratch/patna_last_20_results.json")
