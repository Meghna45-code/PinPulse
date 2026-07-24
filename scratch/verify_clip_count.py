import json

with open("backend/local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

clip_count = sum(1 for p in catalog if p.get("image_vector") and len(p["image_vector"]) == 512)
print(f"Total dresses in catalog: {len(catalog)}")
print(f"Dresses with valid 512-dim CLIP visual vectors: {clip_count}")
