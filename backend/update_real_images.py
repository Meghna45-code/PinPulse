import os
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("update_real_images")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))
FRONTEND_FALLBACK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "catalog_fallback.js"))

def find_best_semantic_image(name: str, description: str, category: str, tags: list) -> str:
    name_lower = name.lower()
    desc_lower = description.lower()
    
    # 1. Sarees (Banarasi, Kasavu, Tussar, Saree)
    if "saree" in name_lower or "saree" in desc_lower:
        if "kasavu" in name_lower or "kasavu" in desc_lower:
            return "https://images.unsplash.com/photo-1610030469668-93535c17b6b3?auto=format&fit=crop&w=600&q=80"  # Kasavu Cream/Gold Saree
        if "pink" in name_lower or "pink" in desc_lower or "fuchsia" in name_lower:
            return "https://images.unsplash.com/photo-1610030469668-93535c17b6b3?auto=format&fit=crop&w=600&q=80"  # Pink Saree
        if "red" in name_lower or "crimson" in name_lower:
            return "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?auto=format&fit=crop&w=600&q=80"  # Red Saree
        return "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80"  # Purple/Navy Silk Saree

    # 2. Waistcoats / Jymphongs
    if "waistcoat" in name_lower or "jymphong" in name_lower:
        return "https://images.unsplash.com/photo-1593030761757-71fae45fa0e7?auto=format&fit=crop&w=600&q=80"  # Black Waistcoat

    # 3. Sherwanis / Kurtas / Men's Festive
    if "sherwani" in name_lower or "kurta" in name_lower:
        if "yellow" in name_lower or "saffron" in name_lower or "haldi" in name_lower:
            return "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80"  # Yellow Kurta
        return "https://images.unsplash.com/photo-1621896338426-302484437a37?auto=format&fit=crop&w=600&q=80"  # Dark Sherwani / Kurta

    # 4. Gowns / Lehengas / Bridal Dresses
    if "lehenga" in name_lower or "lehenga" in desc_lower:
        return "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&w=600&q=80"  # Yellow Lehenga
    if "gown" in name_lower or "gown" in desc_lower:
        return "https://images.unsplash.com/photo-1605787020600-b9ebd5df1d07?auto=format&fit=crop&w=600&q=80"  # Reception Gown
    if "dress" in name_lower or "midi" in name_lower:
        return "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=600&q=80"  # Elegant Party Dress

    # 5. Hoodies / Sweatshirts / Streetwear
    if "hoodie" in name_lower or "sweatshirt" in name_lower or "fleece" in name_lower:
        return "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=600&q=80"  # Streetwear Hoodie
    if "cargo" in name_lower or "streetwear" in name_lower:
        return "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80"  # Skater Cargo Jeans / Streetwear

    # 6. Jackets / Coats / Sweaters
    if "jacket" in name_lower or "coat" in name_lower or "cardigan" in name_lower or "sweater" in name_lower:
        if "leather" in name_lower:
            return "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80"  # Leather Jacket
        if "trench" in name_lower or "coat" in name_lower:
            return "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=600&q=80"  # Winter Trench Coat
        return "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=600&q=80"  # Cardigan / Sweater

    # 7. Shirts / T-shirts
    if "shirt" in name_lower or "tee" in name_lower or "t-shirt" in name_lower:
        if "linen" in name_lower:
            return "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80"  # Linen Shirt
        return "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=600&q=80"  # Casual Tee / Shirt

    # 8. Jeans / Pants / Shorts
    if "jeans" in name_lower or "pants" in name_lower or "shorts" in name_lower:
        return "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80"  # Denim

    # 9. Fallback pools based on category for everything else
    if category == "festive":
        return "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80"
    if category == "winter":
        return "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=600&q=80"
    if category == "streetwear":
        return "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=600&q=80"
    return "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=600&q=80"

def update_images():
    logger.info("Starting semantic fashion image updates...")
    
    # 1. Update local_catalog.json
    if os.path.exists(LOCAL_CATALOG_FILE):
        with open(LOCAL_CATALOG_FILE, "r") as f:
            catalog = json.load(f)
            
        updated_catalog = []
        for p in catalog:
            name = p.get("name", "")
            description = p.get("description", "")
            category = p.get("category", "casual")
            tags = p.get("tags", [])
            
            # Map semantically
            image_url = find_best_semantic_image(name, description, category, tags)
            p["image_url"] = image_url
            updated_catalog.append(p)
            
        with open(LOCAL_CATALOG_FILE, "w") as f:
            json.dump(updated_catalog, f, indent=4)
        logger.info(f"Updated image URLs in local catalog file: {LOCAL_CATALOG_FILE}")
    else:
        logger.warning(f"local_catalog.json not found at {LOCAL_CATALOG_FILE}")

    # 2. Update frontend/src/catalog_fallback.js
    if os.path.exists(FRONTEND_FALLBACK_FILE):
        try:
            with open(LOCAL_CATALOG_FILE, "r") as f:
                prod_data = json.load(f)
            js_content = "export const FALLBACK_PRODUCTS = " + json.dumps(prod_data, indent=2) + ";\n"
            with open(FRONTEND_FALLBACK_FILE, "w") as f:
                f.write(js_content)
            logger.info(f"Successfully rewrote frontend fallback file: {FRONTEND_FALLBACK_FILE}")
        except Exception as e:
            logger.error(f"Failed to update frontend fallback file: {e}")

    # 3. Update Supabase Database
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Connected to Supabase. Updating image URLs in 'products' table...")
            
            with open(LOCAL_CATALOG_FILE, "r") as f:
                catalog = json.load(f)
                
            for p in catalog:
                pid = p["id"]
                image_url = p["image_url"]
                supabase.table("products").update({"image_url": image_url}).eq("id", pid).execute()
                
            logger.info("✅ Successfully updated all image URLs in Supabase products table!")
        except Exception as e:
            logger.error(f"Failed to update Supabase: {e}")
    else:
        logger.warning("Supabase configuration missing. Skipping remote database update.")

if __name__ == "__main__":
    update_images()
