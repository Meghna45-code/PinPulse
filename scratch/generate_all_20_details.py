import sys
import os
import json

sys.path.insert(0, os.path.abspath('backend'))
sys.path.insert(0, os.path.abspath('backend/app'))

from yolo_fashion_cropper import crop_fashion_item

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

with open('scratch/clip_last_20_results.json', 'r', encoding='utf-8') as f:
    last_20 = json.load(f)

artifacts_dir = os.path.abspath(r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0')

full_results = []

for idx, item_info in enumerate(last_20, 113):
    pid = item_info['id']
    cat_item = next((x for x in catalog if x.get('id') == pid), None)
    if not cat_item:
        continue
        
    img_url = cat_item.get('image_url') or cat_item.get('image') or cat_item.get('img') or ""
    prod_link = cat_item.get('product_url') or cat_item.get('myntra_url') or cat_item.get('url') or cat_item.get('link') or f"https://www.myntra.com/{pid}"
    
    local_img_path = ""
    crop_dest_path = ""
    
    if img_url:
        clean_rel = img_url.lstrip('/')
        possible_paths = [
            os.path.abspath(clean_rel),
            os.path.abspath(os.path.join('frontend', 'public', clean_rel)),
            os.path.abspath(os.path.join('frontend', clean_rel))
        ]
        for p in possible_paths:
            if os.path.exists(p):
                local_img_path = p
                break
                
    if local_img_path and os.path.exists(local_img_path):
        try:
            cropped = crop_fashion_item(local_img_path)
            if cropped:
                crop_filename = f"yolo_crop_item_{pid}.jpg"
                crop_dest_path = os.path.join(artifacts_dir, crop_filename)
                cropped.save(crop_dest_path)
        except Exception as e:
            print(f"Error cropping {pid}: {e}")
            
    full_results.append({
        "rank": idx,
        "id": pid,
        "name": cat_item.get('name'),
        "category": cat_item.get('category'),
        "price": cat_item.get('price'),
        "norm_match_pct": item_info.get('norm_match_pct'),
        "raw_cos": item_info.get('raw_cos'),
        "product_link": prod_link,
        "original_image_path": local_img_path,
        "yolo_crop_artifact_path": crop_dest_path
    })

with open('scratch/all_20_yolo_details.json', 'w', encoding='utf-8') as out_f:
    json.dump(full_results, out_f, indent=2)

print(f"Processed all {len(full_results)} items into scratch/all_20_yolo_details.json and saved crops to artifacts.")
