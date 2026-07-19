import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("integrate_images_myntra")

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images_myntra"))
DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images"))

def find_file(directory, prefix):
    # Find any file starting with prefix (case-insensitive prefix search)
    prefix_lower = prefix.lower()
    for f in os.listdir(directory):
        f_name_lower = f.lower()
        # strip extension
        name_part = os.path.splitext(f_name_lower)[0]
        if name_part == prefix_lower:
            return f
        # Handle custom special cases like "44b (2)"
        if name_part.startswith(prefix_lower) and "(" in name_part:
            return f
    return None

def integrate_images():
    if not os.path.exists(SRC_DIR):
        logger.error(f"Source directory {SRC_DIR} not found.")
        return {}
    
    os.makedirs(DEST_DIR, exist_ok=True)
    logger.info(f"Copying images from {SRC_DIR} to {DEST_DIR}...")
    
    mappings = {}
    copied_count = 0
    
    for k in range(1, 51):
        id_a = 100 + (2 * k - 1)
        id_b = 100 + (2 * k)
        
        # 1. Check A image
        file_a = find_file(SRC_DIR, f"{k}a")
        if file_a:
            ext = os.path.splitext(file_a)[1]
            dest_name = f"{id_a}{ext}"
            shutil.copy(os.path.join(SRC_DIR, file_a), os.path.join(DEST_DIR, dest_name))
            mappings[id_a] = f"/images/{dest_name}"
            copied_count += 1
        else:
            logger.warning(f"Missing image for Product ID {id_a} (prefix: {k}a)")
            mappings[id_a] = "/images/1.jpg" # fallback to first image
            
        # 2. Check B image
        file_b = find_file(SRC_DIR, f"{k}b") or find_file(SRC_DIR, f"{k}B")
        if file_b:
            ext = os.path.splitext(file_b)[1]
            dest_name = f"{id_b}{ext}"
            shutil.copy(os.path.join(SRC_DIR, file_b), os.path.join(DEST_DIR, dest_name))
            mappings[id_b] = f"/images/{dest_name}"
            copied_count += 1
        else:
            logger.warning(f"Missing image for Product ID {id_b} (prefix: {k}b)")
            mappings[id_b] = "/images/2.webp" # fallback to second image
            
    logger.info(f"Integration complete. Copied {copied_count} files.")
    return mappings

if __name__ == "__main__":
    integrate_images()
