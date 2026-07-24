import json
import os
import shutil

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

with open('scratch/last_night_agreed_ranking.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

yt_crops = [
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_0.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_1.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_2.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_3.jpg'),
]

formatted = []

for rank, item in enumerate(results[:15], 1):
    pid = item['id']
    name = item['name']
    cat = item['category']
    price = item['price']
    match_pct = item['match_pct']
    buy_link = item['product_link']
    
    # Check if local image artifact exists for this dress
    exts = [".jpg", ".png", ".webp", ".avif"]
    local_img = ""
    for ext in exts:
        p = os.path.join(artifacts_dir, f"catalog_dress_patna_match_{pid}{ext}")
        if os.path.exists(p):
            local_img = p
            break
        p2 = os.path.join(artifacts_dir, f"m_item_{pid}{ext}")
        if os.path.exists(p2):
            local_img = p2
            break
            
    if not local_img:
        # Fallback to copy from root M1..M14 or catalog
        local_img = os.path.join(artifacts_dir, f"catalog_dress_patna_match_{pid}.jpg")
        
    dress_img_link = f"file:///{local_img.replace('\\', '/')}"
    yt_crop_link = f"file:///{yt_crops[(rank - 1) % len(yt_crops)].replace('\\', '/')}"
    
    formatted.append({
        "rank": rank,
        "id": pid,
        "name": name,
        "category": cat,
        "price": price,
        "match_pct": match_pct,
        "yt_crop_link": yt_crop_link,
        "dress_img_link": dress_img_link,
        "buy_link": buy_link
    })

with open('scratch/restored_top15_table.json', 'w', encoding='utf-8') as f:
    json.dump(formatted, f, indent=2)

print("Saved restored Top 15 table to scratch/restored_top15_table.json")
