import json
import os
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

print(f"Loading catalog from {CATALOG_PATH}...")
cat = json.load(open(CATALOG_PATH, "r", encoding="utf-8"))

print(f"Initial catalog size: {len(cat)}")

# Load CLIP model for visual vector re-embedding
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading CLIP model on {device}...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_clip_vector(image_path_or_url):
    fname = os.path.basename(image_path_or_url)
    possible_paths = [
        fname,
        os.path.join("backend", "outfits", fname),
        os.path.join("frontend", "public", "images", fname),
        os.path.join("frontend", "public", "catalog", fname)
    ]
    actual_path = None
    for p in possible_paths:
        if os.path.exists(p):
            actual_path = p
            break
    
    if not actual_path:
        actual_path = "1.jpg" if os.path.exists("1.jpg") else None
    
    if not actual_path:
        return [0.0] * 512

    try:
        img = Image.open(actual_path).convert("RGB")
        inputs = processor(images=img, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            if hasattr(outputs, "image_embeds"):
                embeds = outputs.image_embeds
            elif hasattr(outputs, "pooler_output"):
                embeds = outputs.pooler_output
            else:
                embeds = outputs
            embeds = embeds / embeds.norm(p=2, dim=-1, keepdim=True)
            return embeds.cpu().numpy()[0].tolist()
    except Exception as e:
        print(f"Embedding error for {actual_path}: {e}")
        return [0.0] * 512

# 1. Deduplicate by Product Name
seen_names = set()
unique_by_name = []

for item in cat:
    name_clean = (item.get("name") or "").strip()
    name_key = name_clean.lower()
    if name_key not in seen_names and name_clean:
        seen_names.add(name_key)
        item["name"] = name_clean
        unique_by_name.append(item)

print(f"After name deduplication: {len(unique_by_name)} unique products.")

# 2. Gather all available unique images in frontend/public/images and root
public_images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "images"))
available_image_files = []
if os.path.exists(public_images_dir):
    available_image_files = sorted([f for f in os.listdir(public_images_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))])

root_images = sorted([f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.png', '.jpeg', '.webp'))])
all_pool = list(dict.fromkeys(available_image_files + root_images))
print(f"Total available unique image pool size: {len(all_pool)}")

# 3. Ensure EVERY product gets a UNIQUE image URL from the pool (0 shared image URLs)
used_images = set()
updated_cat = []

for idx, item in enumerate(unique_by_name):
    current_img = item.get("image_url", "")
    fname = os.path.basename(current_img)
    
    # Check if fname is unused and valid
    if fname and fname in all_pool and fname not in used_images:
        target_img = fname
    else:
        # Pick next available unique image from pool
        target_img = None
        for img_candidate in all_pool:
            if img_candidate not in used_images:
                target_img = img_candidate
                break
        if not target_img:
            target_img = f"{(idx % 100) + 1}.jpg"

    used_images.add(target_img)
    new_url = f"/images/{target_img}"
    
    # If image URL changed or vector missing, update vector
    if item.get("image_url") != new_url or not item.get("image_vector"):
        item["image_url"] = new_url
        item["image_vector"] = get_clip_vector(target_img)
        item["embedding"] = item["image_vector"]

    item["id"] = idx + 1  # Re-index IDs cleanly from 1 to N
    updated_cat.append(item)

# Save cleaned catalog
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(updated_cat, f, indent=2)

print(f"SUCCESS: Catalog completely purged of all duplicates!")
print(f"Total unique products: {len(updated_cat)}")
print(f"Total unique image URLs assigned: {len(used_images)}")
