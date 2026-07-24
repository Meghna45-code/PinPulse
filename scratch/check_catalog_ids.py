import json

with open("backend/local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

ids = sorted([item["id"] for item in catalog])
print(f"Total catalog items: {len(catalog)}")
print(f"Max catalog ID: {max(ids)}")
print(f"Items 100+: {[x for x in ids if x >= 100]}")
