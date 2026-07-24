"""
One-shot restore + CLIP merge:
1. Restore 157-product catalog from git commit e062b92
2. Run embed_catalog.py logic inline to merge CLIP image_vectors into all 157 products
"""
import os, sys, json, subprocess, numpy as np

backend_dir = r"C:\Users\HP\OneDrive\Desktop\PinPulse\backend"
catalog_file = os.path.join(backend_dir, "local_catalog.json")

# Step 1: Get 157-product catalog from git
print("Restoring 157-product catalog from git...")
result = subprocess.run(
    ["git", "show", "e062b92:backend/local_catalog.json"],
    cwd=r"C:\Users\HP\OneDrive\Desktop\PinPulse",
    capture_output=True
)
if result.returncode != 0:
    print("Git error:", result.stderr.decode())
    sys.exit(1)

catalog_157 = json.loads(result.stdout.decode("utf-8"))
print(f"Got {len(catalog_157)} products from git")

# Step 2: Load the current 60-product CLIP-embedded catalog
with open(catalog_file, encoding="utf-8") as f:
    clip_60 = json.load(f)

clip_map = {p["id"]: p for p in clip_60}
print(f"Loaded {len(clip_60)} CLIP-embedded products")

# Step 3: Merge CLIP image_vector + embedding into the 157-product catalog
for p in catalog_157:
    pid = p["id"]
    if pid in clip_map:
        p["image_vector"] = clip_map[pid]["image_vector"]
        p["embedding"]    = clip_map[pid]["embedding"]
    else:
        # Products 61-157: use vibe_vector as image_vector fallback
        sys.path.insert(0, backend_dir)
        from embed_catalog import get_vibe_vector
        tags = p.get("tags", [])
        vibe = get_vibe_vector(tags, category_str=p.get("category",""), aesthetic_str="")
        p["image_vector"] = vibe
        if not p.get("embedding"):
            p["embedding"] = vibe

clipped = sum(1 for p in catalog_157 if p.get("image_vector") != p.get("embedding"))
print(f"\nMerge complete: {len(catalog_157)} products")
print(f"  - {len(clip_60)} with real CLIP image_vector (products 1-60)")
print(f"  - {len(catalog_157)-len(clip_60)} with vibe_vector fallback (products 61-157)")

# Step 4: Save clean UTF-8 (no BOM)
with open(catalog_file, "w", encoding="utf-8") as f:
    json.dump(catalog_157, f, indent=4)

print(f"\nSaved {len(catalog_157)}-product merged catalog to {catalog_file}")
