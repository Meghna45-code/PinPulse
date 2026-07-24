import os
import json

with open("backend/local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

print(f"Current catalog items: {len(catalog)}")

root_files = os.listdir(".")
img_files = [f for f in root_files if f.lower().endswith(('.jpg', '.png', '.avif', '.webp'))]
print(f"Total image files in root directory: {len(img_files)}")

# Check items above 98 or 255
high_ids = [f for f in img_files if any(f.startswith(str(i)+".") for i in range(100, 200))]
print(f"Newly uploaded images (100+): {sorted(high_ids)}")
