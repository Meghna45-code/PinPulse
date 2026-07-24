import json
import os

cat_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
js_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

print(f"Reading {cat_file}...")
with open(cat_file, "r", encoding="utf-8") as f:
    catalog = json.load(f)

print(f"Writing {len(catalog)} items to {js_file}...")
js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(catalog, indent=2) + ";\n"

with open(js_file, "w", encoding="utf-8") as f:
    f.write(js_content)

print("Successfully synced local_catalog.json -> catalog_fallback.js!")
