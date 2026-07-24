"""
clip_embed_all.py
=================
Run CLIP image embedding on ALL 157 catalog products using their local image files.

- Products 1-60: frontend/public/catalog/catalog_{id}.jpg  (generated mockup images)
- Products 61-157: frontend/public/images/{id}.webp/.jpg/.avif (real Myntra product photos)

Updates local_catalog.json in-place with real CLIP image_vector for every product.
Also recomputes vibe_vector (embedding) for every product using get_vibe_vector().
"""

import os, sys, json, re
import numpy as np
from PIL import Image

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

CATALOG_FILE  = os.path.join(backend_dir, "local_catalog.json")
CATALOG_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "public", "catalog"))
PRODUCT_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "public", "images"))

# --- Load CLIP model (transformers v5 compatible) ---
print("Loading CLIP model (openai/clip-vit-base-patch32)...")
import torch
from transformers import CLIPModel, CLIPProcessor

torch.set_num_threads(4)
clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
print("CLIP model loaded OK\n")


def get_clip_vec(image_path: str):
    """Return normalized 512-dim CLIP image embedding, or None on failure."""
    try:
        img = Image.open(image_path).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            vision_out  = clip_model.vision_model(pixel_values=inputs["pixel_values"])
            feat_tensor = clip_model.visual_projection(vision_out.pooler_output)
        feat = feat_tensor.detach().cpu().numpy()[0]
        norm = np.linalg.norm(feat)
        return (feat / norm).tolist() if norm > 0 else feat.tolist()
    except Exception as e:
        return None


def find_image(product_id: int, image_url: str) -> str | None:
    """
    Resolve the local file path for a product image.
    Priority:
      1. frontend/public/catalog/catalog_{id}.jpg   (generated mockups, ids 1-60)
      2. frontend/public/images/{id}.<ext>           (real photos, ids 61+)
         where <ext> comes from image_url (webp / jpg / avif / png)
    """
    # Check catalog image first (always for ids 1-60)
    catalog_path = os.path.join(CATALOG_IMG_DIR, f"catalog_{product_id}.jpg")
    if os.path.exists(catalog_path):
        return catalog_path

    # Extract extension from image_url (e.g. /images/61.webp -> webp)
    if image_url:
        basename = os.path.basename(image_url)  # "61.webp"
        img_path = os.path.join(PRODUCT_IMG_DIR, basename)
        if os.path.exists(img_path):
            return img_path

    # Fallback: try common extensions with the product ID
    for ext in ["webp", "jpg", "jpeg", "avif", "png"]:
        p = os.path.join(PRODUCT_IMG_DIR, f"{product_id}.{ext}")
        if os.path.exists(p):
            return p

    return None


# --- Load catalog ---
with open(CATALOG_FILE, encoding="utf-8") as f:
    catalog = json.load(f)
print(f"Loaded {len(catalog)} products from catalog\n")

# Import vibe_vector builder
from embed_catalog import get_vibe_vector

ok_count   = 0
fail_count = 0
no_img     = 0

for p in catalog:
    pid       = p.get("id", 0)
    name      = p.get("name", "?")
    image_url = p.get("image_url", "")

    # Always recompute semantic vibe_vector (text-based)
    vibe_vec = get_vibe_vector(
        p.get("tags", []),
        category_str=p.get("category", ""),
        aesthetic_str=""
    )
    p["embedding"] = vibe_vec

    # Find local image file
    img_path = find_image(pid, image_url)
    if not img_path:
        p["image_vector"] = vibe_vec   # fallback
        no_img += 1
        print(f"  [{pid:3d}] NO IMAGE       -- {name[:45]} (vibe fallback)")
        continue

    clip_vec = get_clip_vec(img_path)
    if clip_vec is not None:
        p["image_vector"] = clip_vec
        ok_count += 1
        print(f"  [{pid:3d}] OK CLIP {os.path.basename(img_path):<20} -- {name[:40]}")
    else:
        p["image_vector"] = vibe_vec   # fallback
        fail_count += 1
        print(f"  [{pid:3d}] FAIL CLIP        -- {name[:40]}")

print(f"\n{'='*60}")
print(f"Done: {ok_count} real CLIP | {fail_count} CLIP errors | {no_img} no image")
print(f"Total: {len(catalog)} products")

# Save merged catalog
with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=4)
print(f"Saved updated catalog to {CATALOG_FILE} - DONE")
