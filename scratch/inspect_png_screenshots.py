import os
import glob
from PIL import Image

png_files = sorted(glob.glob("*.png"))
print(f"Found {len(png_files)} PNG files in root directory:")
for f in png_files:
    try:
        img = Image.open(f)
        size_kb = round(os.path.getsize(f) / 1024, 1)
        print(f"  File: {f:10s} | Dimensions: {img.size} | Size: {size_kb} KB")
    except Exception as e:
        print(f"  Error reading {f}: {e}")
