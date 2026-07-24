import json
import os

with open('scratch/last_night_agreed_ranking.json', 'r', encoding='utf-8') as f:
    full_ranking = json.load(f)

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

yt_crops = [
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_0.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_1.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_2.jpg'),
    os.path.join(artifacts_dir, 'yolo_crop_patna_yt_thumb_3.jpg'),
]

m_results = []

for i in range(1, 15):
    exts = [".jpg", ".webp", ".avif", ".png"]
    local_img_artifact = None
    for ext in exts:
        p = os.path.join(artifacts_dir, f"m_item_{i}{ext}")
        if os.path.exists(p):
            local_img_artifact = p
            break
    if not local_img_artifact:
        local_img_artifact = os.path.join(artifacts_dir, f"m_item_{i}.jpg")
        
    # Search item in full_ranking by id matching i
    found = None
    rank_num = None
    for rank_idx, item in enumerate(full_ranking, 1):
        if item.get('id') == i:
            found = item
            rank_num = rank_idx
            break
            
    if not found:
        # Fallback to rank_idx = i-1
        rank_num = i
        found = full_ranking[i - 1]

    yt_crop_link = f"file:///{yt_crops[(i - 1) % len(yt_crops)].replace('\\', '/')}"
    dress_img_link = f"file:///{local_img_artifact.replace('\\', '/')}"
    buy_link = found.get('product_link') or f"https://www.myntra.com/{found['id']}"

    m_results.append({
        "m_label": f"M{i}",
        "id": found['id'],
        "name": found['name'],
        "category": found['category'],
        "price": found['price'],
        "match_pct": found['match_pct'],
        "rank_out_of_269": rank_num,
        "yt_crop_link": yt_crop_link,
        "dress_img_link": dress_img_link,
        "buy_link": buy_link
    })

print("=== M1 TO M14 RESTORED TABLE (OUT OF 269 DRESSES) ===")
for m in m_results:
    print(f"{m['m_label']} | Rank #{m['rank_out_of_269']:3d} out of 269 | ID {m['id']:3d} | {m['name']:40} | Match: {m['match_pct']}%")

with open('scratch/m1_m14_restored_agreed_table.json', 'w', encoding='utf-8') as f:
    json.dump(m_results, f, indent=2)

print("\nSaved restored agreed M1-M14 table to scratch/m1_m14_restored_agreed_table.json")
