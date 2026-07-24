import os
import shutil
import json

artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'

with open('scratch/all_20_yolo_details.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for item in items:
    pid = item['id']
    orig_path = item.get('original_image_path')
    if orig_path and os.path.exists(orig_path):
        ext = os.path.splitext(orig_path)[1]
        dest_filename = f"catalog_dress_item_{pid}{ext}"
        dest_path = os.path.join(artifacts_dir, dest_filename)
        shutil.copy(orig_path, dest_path)
        item['copied_catalog_image_path'] = dest_path
        print(f"Copied item {pid} original dress image to: {dest_path}")

with open('scratch/all_20_yolo_details.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2)

print("Finished copying all original catalog dress images to artifacts directory.")
