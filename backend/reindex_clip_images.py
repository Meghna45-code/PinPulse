import os
import json
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images"))

print(f"Loading catalog from {CATALOG_PATH}...")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Step 1: Fix known mismatched image URLs
image_fixes = {
    60: "/images/61.webp",      # Denim Collared Shirt Dress
    159: "/images/159.png",     # Zaalima Lehenga
    177: "/images/177.png"      # Libas White Saree
}

for item in catalog:
    pid = item.get("id")
    if pid in image_fixes:
        old_url = item.get("image_url")
        item["image_url"] = image_fixes[pid]
        print(f"Fixed image_url for ID {pid} ({item.get('name')}): {old_url} -> {item['image_url']}")

# Step 2: Initialize PyTorch Fashion-CLIP fine-tuned model
device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_ID = "patrickjohncyh/fashion-clip"
print(f"Loading fine-tuned Fashion-CLIP model ({MODEL_ID}) on device: {device}...")
model = CLIPModel.from_pretrained(MODEL_ID).to(device)
processor = CLIPProcessor.from_pretrained(MODEL_ID)

from yolo_fashion_cropper import crop_fashion_item

def get_clip_image_vector(image_url):
    fname = os.path.basename(image_url)
    fpath = os.path.join(IMAGES_DIR, fname)
    if not os.path.exists(fpath):
        base_name = os.path.splitext(fname)[0]
        for ext in [".jpg", ".png", ".webp", ".avif"]:
            alt_path = os.path.join(IMAGES_DIR, base_name + ext)
            if os.path.exists(alt_path):
                fpath = alt_path
                break
                
    if not os.path.exists(fpath):
        fpath = os.path.join(IMAGES_DIR, "1.jpg")

    try:
        # Crop background clutter, logos, and text overlays using YOLOv8
        img = crop_fashion_item(fpath)
        if img is None:
            img = Image.open(fpath).convert("RGB")
            
        inputs = processor(images=img, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            if hasattr(outputs, "image_embeds"):
                embeds = outputs.image_embeds
            elif hasattr(outputs, "pooler_output"):
                embeds = outputs.pooler_output
            elif isinstance(outputs, torch.Tensor):
                embeds = outputs
            else:
                embeds = outputs[0]
            embeds = embeds / embeds.norm(p=2, dim=-1, keepdim=True)
            return embeds.cpu().numpy()[0].tolist()
    except Exception as e:
        print(f"Error embedding {fpath}: {e}")
        return None

# Step 3: Re-index image_vector for all catalog items using pure CLIP visual extraction
processed_count = 0
for item in catalog:
    img_url = item.get("image_url", "")
    clip_vec = get_clip_image_vector(img_url)
    if clip_vec and len(clip_vec) == 512:
        item["image_vector"] = clip_vec
        processed_count += 1
    else:
        item["image_vector"] = item.get("embedding", [])

print(f"Successfully processed CLIP image_vector for {processed_count}/{len(catalog)} products.")

# Save updated catalog
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print(f"Saved updated catalog to {CATALOG_PATH}!")
