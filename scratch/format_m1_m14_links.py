import json
import os

with open('scratch/m1_m14_rank_comparison.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

yt_crops = [
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_0.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_1.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_2.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_3.jpg'),
]

formatted = []

for idx, item in enumerate(data):
    m_label = item['m_label']
    pid = item['id']
    name = item['name']
    cat = item['category']
    price = item['price']
    old_r = item['old_rank']
    old_p = item['old_match_pct']
    new_r = item['new_rank']
    new_p = item['new_match_pct']
    shift = item['rank_shift']
    buy_link = item['product_link']
    
    dress_img_link = f"file:///{item['image_artifact'].replace('\\', '/')}"
    yt_crop_link = f"file:///{yt_crops[idx % len(yt_crops)].replace('\\', '/')}"
    
    formatted.append({
        "m_label": m_label,
        "id": pid,
        "name": name,
        "category": cat,
        "price": price,
        "old_rank": old_r,
        "old_pct": old_p,
        "new_rank": new_r,
        "new_pct": new_p,
        "shift": shift,
        "yt_crop_link": yt_crop_link,
        "dress_img_link": dress_img_link,
        "buy_link": buy_link
    })

with open('scratch/m1_m14_clean_links.json', 'w', encoding='utf-8') as f:
    json.dump(formatted, f, indent=2)

print("Saved clean text links to scratch/m1_m14_clean_links.json")
