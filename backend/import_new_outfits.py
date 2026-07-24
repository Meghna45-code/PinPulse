"""
import_new_outfits.py
======================
1. Parses 98 new outfits from excel_sheets/Fashion Apparel2.xlsx
2. Copies 66 root image files to frontend/public/images/
3. Assigns new clean Product IDs (starting at 161)
4. Infers fashion tags, category, color, material, price, and zip_codes
5. Appends all new products to local_catalog.json
6. Runs CLIP visual embedding (openai/clip-vit-base-patch32) on ALL catalog items (250+ outfits)
7. Synchronizes local catalog and uploads to Supabase
"""

import os, sys, json, glob, shutil, re
import pandas as pd
import numpy as np
from PIL import Image

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, "app"))

LOCAL_CATALOG_FILE = os.path.join(backend_dir, "local_catalog.json")
DEST_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "public", "images"))
EXCEL_FILE = os.path.join(backend_dir, "..", "excel_sheets", "Fashion Apparel2.xlsx")
ROOT_DIR = os.path.abspath(os.path.join(backend_dir, ".."))

os.makedirs(DEST_IMG_DIR, exist_ok=True)

# ── Load Existing Catalog ──────────────────────────────────────────────────
with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
    catalog = json.load(f)

existing_ids = set(p["id"] for p in catalog)
next_id = max(existing_ids) + 1 if existing_ids else 1
print(f"Loaded existing catalog: {len(catalog)} products | Next ID start: {next_id}")

# ── Copy Root Images to frontend/public/images/ ────────────────────────────
root_imgs = sorted(
    glob.glob(os.path.join(ROOT_DIR, "*.jpg")) +
    glob.glob(os.path.join(ROOT_DIR, "*.png")) +
    glob.glob(os.path.join(ROOT_DIR, "*.webp")) +
    glob.glob(os.path.join(ROOT_DIR, "*.avif"))
)

root_img_map = {}  # index string -> dest_path
print(f"Found {len(root_imgs)} root images to process")

for img_path in root_imgs:
    fname = os.path.basename(img_path)
    dest_path = os.path.join(DEST_IMG_DIR, fname)
    shutil.copy2(img_path, dest_path)
    base_no_ext = os.path.splitext(fname)[0]
    root_img_map[base_no_ext] = f"/images/{fname}"

print(f"Copied {len(root_imgs)} image files to {DEST_IMG_DIR}")

# ── Parse Fashion Apparel2.xlsx ────────────────────────────────────────────
df = pd.read_excel(EXCEL_FILE, header=None)

from import_excel import infer_tags, make_category

new_products = []

for idx, row in df.iterrows():
    vals = [str(v).strip() for v in row.values if pd.notna(v) and str(v).strip() != "nan"]
    if len(vals) < 2:
        continue

    query_desc = vals[0]
    urls = vals[1:]

    for url_idx, product_url in enumerate(urls):
        pid = next_id
        next_id += 1

        tags = infer_tags(query_desc)
        category = make_category(tags)

        # Extract name from Myntra URL or query
        url_parts = product_url.split("/")
        raw_name = ""
        for part in reversed(url_parts):
            if part and not part.isdigit() and part != "buy":
                raw_name = part.replace("-", " ").title()
                break

        if not raw_name or len(raw_name) < 4:
            raw_name = f"{query_desc.title()} - Design {url_idx + 1}"

        # Assign image path
        # Check if root image matching number exists (e.g. 1.jpg, 2.jpg)
        img_key = str(len(new_products) + 1)
        image_url = root_img_map.get(img_key, f"/images/1.jpg")

        # Basic price estimate
        price = 1499.0
        if "saree" in query_desc.lower() or "silk" in query_desc.lower():
            price = 2999.0
        elif "lehenga" in query_desc.lower() or "sherwani" in query_desc.lower():
            price = 5999.0
        elif "shirt" in query_desc.lower() or "tee" in query_desc.lower():
            price = 899.0

        p_dict = {
            "id": pid,
            "name": raw_name[:65],
            "description": f"{query_desc}. Curated from Myntra collection.",
            "category": category,
            "image_url": image_url,
            "product_url": product_url,
            "tags": tags,
            "zip_codes": [],
            "material": "cotton" if "cotton" in query_desc.lower() else ("silk" if "silk" in query_desc.lower() else "blend"),
            "color": "red" if "red" in query_desc.lower() else ("yellow" if "yellow" in query_desc.lower() else "multicolor"),
            "nature": "ethnic" if "ethnic" in tags else "casual",
            "age_range": "18-35",
            "price": price,
            "inventory": 25
        }
        new_products.append(p_dict)

print(f"Parsed {len(new_products)} new outfits from Fashion Apparel2.xlsx")

# ── Merge into main catalog ────────────────────────────────────────────────
catalog.extend(new_products)
print(f"Total catalog size after merge: {len(catalog)} products")

# ── Run CLIP & Vibe Embeddings on ALL Products ────────────────────────────
print("\nLoading CLIP model (openai/clip-vit-base-patch32) for full catalog visual embedding...")
import torch
from transformers import CLIPModel, CLIPProcessor

torch.set_num_threads(4)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
print("CLIP model loaded OK")

from embed_catalog import get_vibe_vector

CATALOG_IMG_DIR = os.path.abspath(os.path.join(backend_dir, "..", "frontend", "public", "catalog"))

def resolve_image_path(product_id: int, image_url: str) -> str | None:
    # 1. catalog/catalog_{id}.jpg
    c_path = os.path.join(CATALOG_IMG_DIR, f"catalog_{product_id}.jpg")
    if os.path.exists(c_path):
        return c_path
    # 2. images/{filename}
    if image_url:
        bname = os.path.basename(image_url)
        i_path = os.path.join(DEST_IMG_DIR, bname)
        if os.path.exists(i_path):
            return i_path
    # 3. images/{id}.<ext>
    for ext in ["jpg", "webp", "png", "avif"]:
        p = os.path.join(DEST_IMG_DIR, f"{product_id}.{ext}")
        if os.path.exists(p):
            return p
    return None

def get_clip_visual_vector(img_path: str):
    try:
        img = Image.open(img_path).convert("RGB")
        inputs = clip_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            vision_out = clip_model.vision_model(pixel_values=inputs["pixel_values"])
            feat_tensor = clip_model.visual_projection(vision_out.pooler_output)
        feat = feat_tensor.detach().cpu().numpy()[0]
        norm = np.linalg.norm(feat)
        return (feat / norm).tolist() if norm > 0 else feat.tolist()
    except Exception as e:
        return None

clip_success = 0
clip_fallback = 0

for p in catalog:
    pid = p.get("id")
    tags = p.get("tags", [])

    # Always compute text vibe vector
    vibe = get_vibe_vector(tags, category_str=p.get("category", ""), aesthetic_str="")
    p["embedding"] = vibe

    # Compute CLIP image vector
    img_path = resolve_image_path(pid, p.get("image_url", ""))
    if img_path:
        cvec = get_clip_visual_vector(img_path)
        if cvec is not None:
            p["image_vector"] = cvec
            clip_success += 1
        else:
            p["image_vector"] = vibe
            clip_fallback += 1
    else:
        p["image_vector"] = vibe
        clip_fallback += 1

print(f"\nCLIP Embedding complete for all {len(catalog)} outfits!")
print(f"  - Real CLIP visual vectors: {clip_success}")
print(f"  - Vibe fallbacks:           {clip_fallback}")

# Save updated local catalog
with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=4)
print(f"\nSaved updated catalog containing {len(catalog)} outfits to {LOCAL_CATALOG_FILE} - DONE")

# Upload to Supabase
from embed_catalog import upload_to_supabase
upload_to_supabase(catalog)
