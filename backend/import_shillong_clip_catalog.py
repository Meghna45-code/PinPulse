import json
import os
import shutil
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

CATALOG_PATH = "backend/local_catalog.json"
PUBLIC_IMG_DIR = "frontend/public/images"
DIST_IMG_DIR = "frontend/dist/images"

os.makedirs(PUBLIC_IMG_DIR, exist_ok=True)
os.makedirs(DIST_IMG_DIR, exist_ok=True)

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    catalog = json.load(f)

print(f"Catalog length before import: {len(catalog)}")

# Find all numbered images in root
root_files = os.listdir(".")
new_images = []
for f in root_files:
    name, ext = os.path.splitext(f)
    if ext.lower() in [".jpg", ".png", ".avif", ".webp"] and name.isdigit():
        new_images.append((int(name), f))

new_images.sort(key=lambda x: x[0])
print(f"Found {len(new_images)} numbered images in root: {[x[1] for x in new_images if x[0] >= 100]}")

# Load CLIP model for embedding generation
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading CLIP model on {device}...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

catalog_dict = {item["id"]: item for item in catalog}

# Definitions for Shillong (Meghalaya) and traditional dresses
shillong_dresses = {
    100: {"name": "Authentic Khasi Traditional Jainsem Silk Suit", "category": "Meghalaya Traditional", "tags": ["shillong", "khasi", "jainsem", "silk", "nongkrem", "traditional", "meghalaya"], "zip_codes": ["793001"]},
    101: {"name": "Garo Traditional Dakmanda Handloom Dress", "category": "Garo Traditional", "tags": ["shillong", "garo", "dakmanda", "wangala", "handloom", "meghalaya"], "zip_codes": ["793001"]},
    103: {"name": "Wangala Tribal Beaded Festive Jacket", "category": "Meghalaya Tribal", "tags": ["shillong", "wangala", "beaded", "jacket", "tribal", "festive"], "zip_codes": ["793001"]},
    104: {"name": "Shillong Pastel Cherry Blossom Linen Maxi", "category": "Contemporary Fusion", "tags": ["shillong", "cherry_blossom", "pastel", "linen", "coastal", "casual"], "zip_codes": ["793001"]},
    105: {"name": "Khasi Gold-Embroidered Velvet Festive Top", "category": "Meghalaya Traditional", "tags": ["shillong", "khasi", "velvet", "gold", "festive", "traditional"], "zip_codes": ["793001"]},
    106: {"name": "Jaintia Pniam Handwoven Silk Shawl & Kurti", "category": "Meghalaya Handloom", "tags": ["shillong", "jaintia", "silk", "handwoven", "shawl", "meghalaya"], "zip_codes": ["793001"]},
    107: {"name": "Traditional Khasi Red Zari Border Wrap", "category": "Meghalaya Traditional", "tags": ["shillong", "khasi", "zari", "wrap", "red", "ethnic"], "zip_codes": ["793001"]},
    108: {"name": "Nongkrem Dance Silk Gold Brocade Kurta Set", "category": "Meghalaya Festive", "tags": ["shillong", "nongkrem", "silk", "brocade", "festive", "ethnic"], "zip_codes": ["793001"]},
    109: {"name": "Highland Woolen Knitted Cardigan & Stole", "category": "Shillong Winter", "tags": ["shillong", "woolen", "winter", "knitted", "cardigan", "cozy"], "zip_codes": ["793001"]},
    110: {"name": "Garo Tribal Diamond Ikat Handloom Kurti", "category": "Garo Handloom", "tags": ["shillong", "garo", "ikat", "handloom", "tribal", "meghalaya"], "zip_codes": ["793001"]},
    111: {"name": "Shillong Autumn Festival Floral Chiffon Gown", "category": "Contemporary Fusion", "tags": ["shillong", "autumn", "floral", "chiffon", "gown", "festive"], "zip_codes": ["793001"]},
    112: {"name": "Meghalaya Eri Silk Hand-Spun Ethnic Scarf Set", "category": "Meghalaya Handloom", "tags": ["shillong", "eri_silk", "silk", "sustainable", "handspun", "meghalaya"], "zip_codes": ["793001"]},
    113: {"name": "Meghalaya Tribal Handwoven Fiber Vest", "category": "Meghalaya Tribal", "tags": ["shillong", "tribal", "handwoven", "meghalaya"], "zip_codes": ["793001"]},
    114: {"name": "Khasi Coral & Gold Bead Festive Stole Set", "category": "Meghalaya Festive", "tags": ["shillong", "khasi", "bead", "stole", "gold"], "zip_codes": ["793001"]},
    115: {"name": "Shillong Indie Boho Cotton Midi Dress", "category": "Contemporary Fusion", "tags": ["shillong", "boho", "cotton", "midi"], "zip_codes": ["793001"]},
    116: {"name": "Garo Handspun Cotton Wrap Skirt", "category": "Garo Traditional", "tags": ["shillong", "garo", "wrap", "skirt"], "zip_codes": ["793001"]},
    117: {"name": "Meghalaya Heritage Silk Saree", "category": "Meghalaya Traditional", "tags": ["shillong", "silk", "saree", "heritage"], "zip_codes": ["793001"]},
    118: {"name": "Royal Rajputana Bandhani Silk Dupatta", "category": "Rajasthani Traditional", "tags": ["rajasthan", "bandhani", "silk", "dupatta", "ethnic"], "zip_codes": ["302001"]},
    120: {"name": "Rajasthani Gota Patti Ethnic Lehenga Suit", "category": "Rajasthani Festive", "tags": ["rajasthan", "gota_patti", "lehenga", "teej", "ethnic"], "zip_codes": ["302001"]},
    121: {"name": "Jaipur Block Print Cotton Anarkali Set", "category": "Rajasthani Handloom", "tags": ["rajasthan", "block_print", "jaipur", "anarkali", "cotton"], "zip_codes": ["302001"]},
    122: {"name": "Marwar Mirror Work Traditional Choli", "category": "Rajasthani Traditional", "tags": ["rajasthan", "mirror_work", "choli", "gangaur"], "zip_codes": ["302001"]},
    123: {"name": "Desert Rose Silk Angrakha Kurta Set", "category": "Rajasthani Festive", "tags": ["rajasthan", "angrakha", "silk", "kurta", "pushkar"], "zip_codes": ["302001"]}
}

updated_count = 0
for img_id, filename in new_images:
    pub_path = os.path.join(PUBLIC_IMG_DIR, filename)
    dist_path = os.path.join(DIST_IMG_DIR, filename)
    shutil.copy(filename, pub_path)
    shutil.copy(filename, dist_path)
    
    img_rel_path = f"/images/{filename}"
    
    # Generate CLIP image embedding vector (512-dim)
    try:
        raw_img = Image.open(filename).convert("RGB")
        inputs = processor(images=raw_img, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            if hasattr(outputs, "image_embeds") and outputs.image_embeds is not None:
                image_features = outputs.image_embeds
            elif hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
                image_features = outputs.pooler_output
            elif torch.is_tensor(outputs):
                image_features = outputs
            else:
                image_features = outputs[0]
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            vec = image_features.cpu().numpy().flatten().tolist()
    except Exception as e:
        print(f"Error computing CLIP vector for {filename}: {e}")
        vec = [0.1] * 512

    if img_id in catalog_dict:
        item = catalog_dict[img_id]
        item["image_url"] = img_rel_path
        item["image_vector"] = vec
        item["embedding"] = vec
        updated_count += 1
    else:
        # Create new catalog entry
        preset_info = shillong_dresses.get(img_id, {
            "name": f"Regional Special Dress #{img_id}",
            "category": "Regional Special",
            "tags": ["regional", "ethnic", "fashion"],
            "zip_codes": ["793001", "302001"]
        })
        new_item = {
            "id": img_id,
            "name": preset_info["name"],
            "category": preset_info["category"],
            "description": f"{preset_info['name']} crafted with authentic regional fabrics.",
            "image_url": img_rel_path,
            "product_url": f"https://www.myntra.com/dress-{img_id}",
            "tags": preset_info["tags"],
            "zip_codes": preset_info["zip_codes"],
            "price": (img_id * 37) % 2500 + 1299,
            "image_vector": vec,
            "embedding": vec
        }
        catalog.append(new_item)
        catalog_dict[img_id] = new_item
        updated_count += 1

print(f"Total updated/inserted catalog items: {updated_count}")

# Save updated catalog
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)

print(f"Catalog length after import: {len(catalog)}")
