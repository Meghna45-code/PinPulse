"""
update_products_71_90_clip.py
==============================
1. Copies new root images (71.jpg to 90.jpg/.png) to frontend/public/images/ and frontend/dist/images/
2. Updates products 71 to 90 in local_catalog.json to use these exact new image filenames
3. Runs PyTorch CLIP model (openai/clip-vit-base-patch32) on products 71-90 to extract real visual image_vectors from the new pictures
4. Saves local_catalog.json and uploads to Supabase SQL database
5. Cleans up root image files
"""

import os, sys, json, glob, shutil
import numpy as np
from PIL import Image

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, "app"))

LOCAL_CATALOG_FILE = os.path.join(backend_dir, "local_catalog.json")
DEST_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "public", "images"))
DIST_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "dist", "images"))
ROOT_DIR = os.path.abspath(os.path.join(backend_dir, ".."))

os.makedirs(DEST_IMG_DIR, exist_ok=True)
if os.path.exists(os.path.abspath(os.path.join(backend_dir, "..", "frontend", "dist"))):
    os.makedirs(DIST_IMG_DIR, exist_ok=True)

# ── Load Catalog ──────────────────────────────────────────────────────────
with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
    catalog = json.load(f)

cat_map = {p["id"]: p for p in catalog}

# ── Find New Root Images (71-90) ──────────────────────────────────────────
root_imgs = sorted(
    glob.glob(os.path.join(ROOT_DIR, "*.jpg")) +
    glob.glob(os.path.join(ROOT_DIR, "*.png")) +
    glob.glob(os.path.join(ROOT_DIR, "*.webp"))
)

print(f"Found {len(root_imgs)} newly uploaded root images (71-90)")

image_updates = {}  # pid -> filename

for img_path in root_imgs:
    fname = os.path.basename(img_path)  # e.g. "71.jpg", "81.png"
    base_no_ext = os.path.splitext(fname)[0]
    if base_no_ext.isdigit():
        pid = int(base_no_ext)
        if 71 <= pid <= 90 and pid in cat_map:
            # Copy to public/images and dist/images
            dest_pub = os.path.join(DEST_IMG_DIR, fname)
            shutil.copy2(img_path, dest_pub)
            if os.path.exists(DIST_IMG_DIR):
                shutil.copy2(img_path, os.path.join(DIST_IMG_DIR, fname))

            img_rel_url = f"/images/{fname}"
            cat_map[pid]["image_url"] = img_rel_url
            image_updates[pid] = (fname, img_path)
            print(f"  Mapped Product {pid:2d} ({cat_map[pid]['name'][:30]}) -> {img_rel_url}")

print(f"\nUpdated image_url for {len(image_updates)} products (IDs 71-90)")

# ── Load CLIP Model ───────────────────────────────────────────────────────
print("\nLoading CLIP model (openai/clip-vit-base-patch32) for new picture embeddings...")
import torch
from transformers import CLIPModel, CLIPProcessor

torch.set_num_threads(4)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
print("CLIP model loaded OK")

def get_clip_visual_vector(img_file_path: str):
    try:
        img = Image.open(img_file_path).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            vision_out = clip_model.vision_model(pixel_values=inputs["pixel_values"])
            feat_tensor = clip_model.visual_projection(vision_out.pooler_output)
        feat = feat_tensor.detach().cpu().numpy()[0]
        norm = np.linalg.norm(feat)
        return (feat / norm).tolist() if norm > 0 else feat.tolist()
    except Exception as e:
        print(f"Error extracting CLIP embedding for {img_file_path}: {e}")
        return None

clip_ok = 0
for pid, (fname, img_path) in image_updates.items():
    cvec = get_clip_visual_vector(img_path)
    if cvec is not None:
        cat_map[pid]["image_vector"] = cvec
        clip_ok += 1
        print(f"  ✓ Generated CLIP visual vector for Product {pid:2d} ({fname}) — dim={len(cvec)}")
    else:
        print(f"  ✗ Failed CLIP vector for Product {pid:2d}")

print(f"\nCLIP embeddings generated for {clip_ok} / {len(image_updates)} new pictures!")

# Save catalog
with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=4)
print(f"Saved updated local_catalog.json ({len(catalog)} total products) - DONE")

# Upload to Supabase
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))
from embed_catalog import upload_to_supabase

res = upload_to_supabase(catalog)
print(f"Supabase upload result: {res}")

# Cleanup root image copies
for img_path in root_imgs:
    try:
        os.remove(img_path)
    except Exception:
        pass
print("Workspace root cleaned up OK.")
