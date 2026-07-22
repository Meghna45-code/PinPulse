import os
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("compress_images")

IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images"))
MAX_WIDTH = 400

def compress_images():
    if not os.path.exists(IMAGES_DIR):
        logger.error(f"Images directory {IMAGES_DIR} not found.")
        return
        
    files = os.listdir(IMAGES_DIR)
    logger.info(f"Scanning {len(files)} files in {IMAGES_DIR} for compression...")
    
    saved_bytes = 0
    optimized_count = 0
    
    for idx, fname in enumerate(files):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.avif']:
            continue
            
        img_path = os.path.join(IMAGES_DIR, fname)
        old_size = os.path.getsize(img_path)
        
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                
                # Resize if width exceeds MAX_WIDTH
                if w > MAX_WIDTH:
                    new_w = MAX_WIDTH
                    new_h = int(h * (MAX_WIDTH / w))
                    # Resize while preserving ratio
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    resized = True
                else:
                    resized = False
                
                # Compress and overwrite
                # Convert to RGB if format requires and mode is RGBA
                save_kwargs = {}
                save_format = img.format if img.format else "JPEG"
                
                if ext in ['.jpg', '.jpeg']:
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    save_kwargs = {'quality': 80, 'optimize': True}
                    save_format = "JPEG"
                elif ext == '.webp':
                    save_kwargs = {'quality': 80, 'method': 4}
                    save_format = "WEBP"
                elif ext == '.png':
                    save_kwargs = {'optimize': True, 'compress_level': 8}
                    save_format = "PNG"
                elif ext == '.avif':
                    # Pillow requires additional plugins for AVIF, fallback to standard save
                    save_kwargs = {'quality': 80}
                    save_format = "AVIF"
                
                # Temporary save path to check size before overwriting
                temp_path = img_path + ".tmp"
                img.save(temp_path, format=save_format, **save_kwargs)
                new_size = os.path.getsize(temp_path)
                
                if new_size < old_size or resized:
                    os.replace(temp_path, img_path)
                    saved_bytes += (old_size - new_size)
                    optimized_count += 1
                    if idx % 20 == 0:
                        logger.info(f"  [{idx}/{len(files)}] Optimized {fname}: {old_size/1024:.1f}KB -> {new_size/1024:.1f}KB")
                else:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        except Exception as e:
            logger.error(f"Failed to compress {fname}: {e}")
            
    logger.info(f"Compression complete! Optimized {optimized_count} files, saving {saved_bytes / (1024*1024):.2f} MB in total.")

if __name__ == "__main__":
    compress_images()
