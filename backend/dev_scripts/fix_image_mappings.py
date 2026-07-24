import json
import os
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

CATALOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

print(f"Loading catalog from {CATALOG_PATH}...")
cat = json.load(open(CATALOG_PATH, "r", encoding="utf-8"))

# Load PyTorch CLIP model for re-embedding updated/fixed items
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading CLIP model on {device}...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_clip_image_vector(image_path_or_url):
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
        # Fallback default image
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
        print(f"Error embedding {actual_path}: {e}")
        return [0.0] * 512

# 1. Deduplicate by (name, image_url)
seen_keys = set()
unique_cat = []
for item in cat:
    key = (item.get("name", "").strip().lower(), item.get("image_url", "").strip())
    if key not in seen_keys:
        seen_keys.add(key)
        unique_cat.append(item)

print(f"Deduplicated catalog from {len(cat)} to {len(unique_cat)} items.")

# 2. Fix Athleisure / Hoodie items and erroneous saree images
# Let's inspect root images to assign real hoodie / athleisure / jacket images to hoodie/sweatshirt items!
# Available root images with modern/streetwear/athleisure look:
# 11.jpg, 26.jpg, 57.jpg, 58.jpg, 67.jpg, 100.jpg..124.jpg

athleisure_images = ["58.jpg", "26.jpg", "11.jpg", "57.jpg", "67.jpg", "100.jpg", "101.jpg", "103.jpg", "104.jpg", "105.jpg"]

for item in unique_cat:
    name_lower = item.get("name", "").lower()
    tags = item.get("tags", [])
    img_url = item.get("image_url", "")
    
    # If item is a hoodie / sweatshirt / tracksuit / athleisure, ensure proper athleisure tags and image!
    if any(k in name_lower for k in ["hooded", "sweatshirt", "hoodie", "tracksuit", "athleisure", "jogger", "sneakers", "activewear", "pullover", "windcheater"]):
        # Update tags to include Urban Athleisure keywords
        ath_tags = ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "hoodie", "sweatshirt", "gym", "jogger", "streetwear"]
        for t in ath_tags:
            if t not in tags:
                tags.append(t)
        item["tags"] = tags
        item["category"] = "Urban Athleisure"
        item["nature"] = "Urban Athleisure"
        
        # If it was assigned saree image (/images/1.jpg), assign a proper winter/athleisure image!
        if "1.jpg" in img_url or "2.jpg" in img_url or "3.jpg" in img_url or "5.jpg" in img_url:
            idx = (item.get("id", 0)) % len(athleisure_images)
            new_img = f"/images/{athleisure_images[idx]}"
            item["image_url"] = new_img
            print(f"Fixed image for '{item.get('name')}': {img_url} -> {new_img}")
            item["image_vector"] = get_clip_image_vector(athleisure_images[idx])
            item["embedding"] = item["image_vector"]

    # If an item has /images/1.jpg (Saree) but title is coat, jacket, dress, boots, ring, etc.
    elif "1.jpg" in img_url and not any(k in name_lower for k in ["saree", "lehenga", "dupatta", "ilkal"]):
        # Re-assign image based on item type
        if any(k in name_lower for k in ["coat", "jacket", "trench", "pea coat"]):
            new_img = "/images/57.jpg"
        elif any(k in name_lower for k in ["sweater", "pullover", "cardigan"]):
            new_img = "/images/26.jpg"
        elif any(k in name_lower for k in ["boot", "boots", "heel"]):
            new_img = "/images/53.jpg"
        elif any(k in name_lower for k in ["dress", "gown", "maxi"]):
            new_img = "/images/15.jpg"
        elif any(k in name_lower for k in ["blazer", "tuxedo", "suit"]):
            new_img = "/images/20.jpg"
        else:
            new_img = f"/images/{(item.get('id', 1) % 60) + 1}.jpg"
            
        item["image_url"] = new_img
        print(f"Re-mapped erroneous image for '{item.get('name')}': {img_url} -> {new_img}")
        fname = os.path.basename(new_img)
        item["image_vector"] = get_clip_image_vector(fname)
        item["embedding"] = item["image_vector"]

# 3. Add explicit dedicated Athleisure items if needed to enrich Athleisure vibe
athleisure_products = [
    {
        "id": 301,
        "name": "Puma Urban Fleece Oversized Athleisure Hoodie",
        "category": "Urban Athleisure",
        "price": 2499,
        "image_url": "http://localhost:8000/outfits/100.jpg",
        "tags": ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "hoodie", "sweatshirt", "gym", "jogger", "streetwear"],
        "zip_codes": ["800008", "682001", "752001", "793001", "302001"],
        "aov_range": "mid",
        "season": ["autumn", "winter"],
        "material": "fleece cotton",
        "color": "black"
    },
    {
        "id": 302,
        "name": "Nike Dri-FIT Tech Fleece Joggers & Track Jacket",
        "category": "Urban Athleisure",
        "price": 3999,
        "image_url": "http://localhost:8000/outfits/101.jpg",
        "tags": ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "gym", "jogger", "athletic"],
        "zip_codes": ["800008", "682001", "752001", "793001", "302001"],
        "aov_range": "high",
        "season": ["autumn", "winter", "spring"],
        "material": "tech fleece",
        "color": "grey"
    },
    {
        "id": 303,
        "name": "Adidas Originals Ribbed Athleisure Crop Top & Sweatpants",
        "category": "Urban Athleisure",
        "price": 2799,
        "image_url": "http://localhost:8000/outfits/103.jpg",
        "tags": ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "sneakers", "ribbed", "gym", "jogger", "gen-z"],
        "zip_codes": ["800008", "682001", "752001", "793001", "302001"],
        "aov_range": "mid",
        "season": ["summer", "autumn"],
        "material": "cotton blend",
        "color": "olive"
    },
    {
        "id": 304,
        "name": "Under Armour Seamless Active Gym Workout Set",
        "category": "Urban Athleisure",
        "price": 3299,
        "image_url": "http://localhost:8000/outfits/104.jpg",
        "tags": ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "athletic", "gym", "seamless"],
        "zip_codes": ["800008", "682001", "752001", "793001", "302001"],
        "aov_range": "high",
        "season": ["all"],
        "material": "spandex poly",
        "color": "navy"
    }
]

# Generate vectors for new Athleisure items
for item in athleisure_products:
    if not any(x.get("id") == item["id"] for x in unique_cat):
        fname = os.path.basename(item["image_url"])
        item["image_vector"] = get_clip_image_vector(fname)
        item["embedding"] = item["image_vector"]
        unique_cat.append(item)

# Save updated catalog
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(unique_cat, f, indent=2)

print(f"Successfully updated local_catalog.json! Total items now: {len(unique_cat)}")
