"""
update_fallback_catalog.py
--------------------------
Regenerates the frontend/src/catalog_fallback.js with the correct
local image URLs (/images/<id>.<ext>) for products 1-100.

This script reads local_catalog.json and replaces only the image_url fields
in catalog_fallback.js without regenerating the huge embeddings.
"""
import os
import re
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("update_fallback")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_FILE = os.path.join(BASE_DIR, "backend", "local_catalog.json")
FALLBACK_FILE = os.path.join(BASE_DIR, "frontend", "src", "catalog_fallback.js")
IMAGES_DIR = os.path.join(BASE_DIR, "Pictures of fashion apparel 2")


def build_image_map():
    """Returns {id_number: '/images/filename'} for local images."""
    img_map = {}
    for fname in os.listdir(IMAGES_DIR):
        name_no_ext = os.path.splitext(fname)[0]
        try:
            num = int(name_no_ext)
            img_map[num] = f"/images/{fname}"
        except ValueError:
            pass
    return img_map


def update_fallback():
    img_map = build_image_map()
    logger.info(f"Built image map with {len(img_map)} local images.")

    # Read the fallback JS file
    with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # We'll do targeted replacements for each product that has a local image.
    # Strategy: find each object block and replace its image_url if it matches
    # The pattern: look for  "id": <N>,\n ... "image_url": "...",
    # and replace the image_url value when id is in img_map.

    updated_count = 0

    def replace_image_url(match):
        nonlocal updated_count
        product_id_str = match.group(1)
        try:
            pid = int(product_id_str)
        except ValueError:
            return match.group(0)

        if pid in img_map:
            old_block = match.group(0)
            old_url = match.group(2)
            new_url = img_map[pid]
            if old_url != new_url:
                new_block = old_block.replace(f'"{old_url}"', f'"{new_url}"', 1)
                updated_count += 1
                return new_block
        return match.group(0)

    # Pattern: capture id number and image_url within a product block
    # Match: "id": <N>,\n followed by optional lines before "image_url": "<url>"
    # Since the structure is consistent ({  "id": N,\n ... "image_url": "...",) 
    # we use a non-greedy approach within a reasonable window
    pattern = re.compile(
        r'"id":\s*(\d+),\s*\n(?:[^\n]*\n){0,5}?\s*"image_url":\s*"([^"]*)"',
        re.MULTILINE
    )

    new_content = pattern.sub(replace_image_url, content)

    with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    logger.info(f"Updated {updated_count} image_url entries in catalog_fallback.js")
    print(f"Done! Updated {updated_count} image_url entries.")


if __name__ == "__main__":
    update_fallback()
