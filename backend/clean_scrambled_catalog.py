import os
import json
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

cat_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
js_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))
images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images"))

print(f"Loading catalog from {cat_path}...")
with open(cat_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading CLIP model on device: {device}...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

verified_catalog = []
removed_count = 0

for item in catalog:
    name = item.get("name", "")
    img_url = item.get("image_url", "")
    fname = os.path.basename(img_url)
    fpath = os.path.join(images_dir, fname)
    if not os.path.exists(fpath):
        base_name = os.path.splitext(fname)[0]
        for ext in [".jpg", ".png", ".webp", ".avif"]:
            alt = os.path.join(images_dir, base_name + ext)
            if os.path.exists(alt):
                fpath = alt
                break

    if not os.path.exists(fpath):
        print(f"Removing ID {item.get('id')} ('{name}'): Image file not found {fname}")
        removed_count += 1
        continue

    try:
        img = Image.open(fpath).convert("RGB")
        inputs = processor(text=[name], images=img, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            img_embeds = outputs.image_embeds / outputs.image_embeds.norm(p=2, dim=-1, keepdim=True)
            txt_embeds = outputs.text_embeds / outputs.text_embeds.norm(p=2, dim=-1, keepdim=True)
            sim = float((img_embeds @ txt_embeds.T)[0][0].cpu().numpy())
            
            # Require minimum cross-modal alignment between title and image
            if sim >= 0.21:
                item["text_image_alignment"] = sim
                verified_catalog.append(item)
            else:
                print(f"Removing ID {item.get('id')} ('{name}'): Scrambled mismatch (Sim: {sim:.3f}, Image: {fname})")
                removed_count += 1
    except Exception as e:
        print(f"Error checking ID {item.get('id')}: {e}")

print(f"\nCatalog Cleaned: Kept {len(verified_catalog)} verified products | Removed {removed_count} scrambled products.")

# Save clean local_catalog.json
with open(cat_path, "w", encoding="utf-8") as f:
    json.dump(verified_catalog, f, indent=2)

print(f"Saved verified catalog to {cat_path}!")

# Sync to catalog_fallback.js
js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(verified_catalog, indent=2) + ";\n"
with open(js_file, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Synced {len(verified_catalog)} verified products to {js_file}!")
