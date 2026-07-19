import json

with open("backend/local_catalog.json", "r") as f:
    data = json.load(f)

print(f"Total products: {len(data)}")
print("\nFirst 15 products - id & image_url:")
for p in data[:15]:
    print(f"  id={p['id']:>4}  image_url={p.get('image_url', 'NONE')[:80]}")

print("\n--- Checking how many use placehold.co vs real URLs ---")
placehold = sum(1 for p in data if "placehold.co" in str(p.get("image_url", "")))
myntra = sum(1 for p in data if "myntra" in str(p.get("image_url", "")).lower())
local = sum(1 for p in data if "/images/" in str(p.get("image_url", "")) or "localhost" in str(p.get("image_url", "")))
no_img = sum(1 for p in data if not p.get("image_url"))
print(f"  placehold.co (fallback): {placehold}")
print(f"  myntra CDN:              {myntra}")
print(f"  localhost/local:         {local}")
print(f"  no image_url:            {no_img}")
print(f"  other:                   {len(data) - placehold - myntra - local - no_img}")
