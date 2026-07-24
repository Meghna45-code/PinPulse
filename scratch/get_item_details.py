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

print("Checking details for the lowest CLIP fashion matches:")
for item_info in last_20[-5:]: # Bottom 5
    pid = item_info['id']
    cat_item = next((x for x in catalog if x.get('id') == pid), None)
    if cat_item:
        print("="*60)
        print(f"ID {pid}: {cat_item.get('name')}")
        print(f"  Category: {cat_item.get('category')}")
        print(f"  Price: Rs.{cat_item.get('price')}")
        print(f"  CLIP Match: {item_info.get('norm_match_pct')}% (Raw Cosine: {item_info.get('raw_cos'):.4f})")
        
        # Images & links
        img_url = cat_item.get('image_url') or cat_item.get('image') or cat_item.get('img')
        prod_link = cat_item.get('product_url') or cat_item.get('myntra_url') or cat_item.get('url') or cat_item.get('link') or f"https://www.myntra.com/{cat_item.get('id')}"
        print(f"  Image relative path / URL: {img_url}")
        print(f"  Product Link: {prod_link}")
        
        # Check if local image exists
        if img_url:
            local_img_path = os.path.abspath(img_url.lstrip('/'))
            if not os.path.exists(local_img_path):
                local_img_path = os.path.abspath(os.path.join('frontend', 'public', img_url.lstrip('/')))
            print(f"  Local Image File Path: {local_img_path} (Exists: {os.path.exists(local_img_path)})")
            
            # Crop image using YOLO and save thumbnail in artifacts/scratch
            if os.path.exists(local_img_path):
                cropped = crop_fashion_item(local_img_path)
                if cropped:
                    out_crop_path = os.path.abspath(f"scratch/yolo_crop_item_{pid}.jpg")
                    cropped.save(out_crop_path)
                    print(f"  YOLO Crop Thumbnail saved to: {out_crop_path}")
