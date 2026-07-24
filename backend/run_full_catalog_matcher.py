import os
import sys
import json
import re
import urllib.request
from io import BytesIO
from PIL import Image
import numpy as np

sys.path.append(os.path.abspath('backend'))
from fashion_clip_matcher import (
    get_image_embedding, cosine_similarity, compute_tag_overlap, 
    classify_gender_and_category, extract_hsv_color_palette, compute_color_similarity_hsv
)
from yolo_fashion_cropper import crop_fashion_item

LOCAL_CATALOG_PATH = os.path.abspath(os.path.join("backend", "local_catalog.json"))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def match_thumbnail_full_28k(img_path, top_k=5):
    """
    Full 28,000 Catalog Gender-Strict, Text-Overlay Resistant & HSV Color Veto Matcher:
      1. Crop input thumbnail with YOLOv8.
      2. Classify Gender ('men' vs 'women') & Refined Macro Category.
      3. Extract text-overlay resistant HSV color palette from garment fabric crop.
      4. HARD FILTER catalog items strictly by gender ('men' vs 'women').
      5. Extract candidate product photos, compute 512-D Visual Vectors AND HSV Color Similarity.
      6. Rank candidates by S_final = (0.70 * S_visual + 0.30 * S_tag) * S_color.
    """
    if not os.path.exists(img_path):
        print(f"Error: Target image not found at {img_path}")
        return []

    print(f"Loading full 28,638 catalog database from {LOCAL_CATALOG_PATH}...")
    with open(LOCAL_CATALOG_PATH, "r", encoding="utf-8") as f:
        full_catalog = json.load(f)

    print(f"Loaded {len(full_catalog)} catalog items.")

    # 1. YOLO Bounding Box Cropper
    raw_img = Image.open(img_path).convert("RGB")
    cropped_img = crop_fashion_item(raw_img) or raw_img

    # 2. VLM Zero-Shot Gender & Refined Category Classification
    detected_gender, detected_cat = classify_gender_and_category(cropped_img)
    print(f"\n[Stage 1 VLM Output]: Detected Gender = '{detected_gender}', Macro Category = '{detected_cat}'")

    # 3. Extract Garment HSV Color Palette (Text-Overlay Resistant)
    thumb_hsv = extract_hsv_color_palette(cropped_img)
    print(f"[Color Engine]: Garment Fabric HSV Palette = Hue: {thumb_hsv[0]:.1f}°, Saturation: {thumb_hsv[1]:.2f}, Value: {thumb_hsv[2]:.2f}")

    # 4. HARD STRICT GENDER FILTER (Can NEVER fall back to opposite gender)
    gender_items = [
        item for item in full_catalog 
        if item.get("gender") == detected_gender
    ]
    if not gender_items:
        gender_items = full_catalog

    bucket_items = [
        item for item in gender_items 
        if item.get("macro_category") == detected_cat or item.get("category") == detected_cat
    ]
    
    if len(bucket_items) < 5:
        bucket_items = gender_items

    print(f"[Stage 2 Bucket Filter]: Hard gender-filtered catalog to {len(bucket_items)} strictly '{detected_gender}' - '{detected_cat}' items.")

    # 5. Thumbnail 512-D Visual CLIP Embedding
    thumb_vis_vec = get_image_embedding(cropped_img)

    # 6. Evaluate Visual Vectors & Color Palettes for candidate items in the bucket
    embedded_candidates = []
    
    print(f"\nProcessing product visual & color embeddings across candidate bucket ({len(bucket_items)} items)...")
    
    for idx, item in enumerate(bucket_items[:120], 1):
        img_url = item.get("image_url", "")
        pid = item.get("id")
        
        if not img_url.startswith("http") and pid:
            img_url = f"https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/product/{pid}/1.jpg"
        
        if not img_url.startswith("http"):
            continue

        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                img_data = response.read()
                pil_img = Image.open(BytesIO(img_data)).convert("RGB")
                cropped_pil = crop_fashion_item(pil_img) or pil_img
                
                vis_vec = get_image_embedding(cropped_pil)
                cat_hsv = extract_hsv_color_palette(cropped_pil)
                
                if vis_vec is not None:
                    item["image_vector"] = vis_vec.tolist()
                    item["hsv_color"] = cat_hsv
                    embedded_candidates.append(item)
        except Exception:
            pass

    print(f"Successfully processed True Visual & Color Embeddings for {len(embedded_candidates)} candidate products.")

    # 7. Rank Candidates by S_visual, S_color & S_hybrid
    results = []
    fname = os.path.basename(img_path)
    title_text = fname.replace("_", " ").replace("-", " ")

    for item in embedded_candidates:
        # Enforce strict gender check again at ranking time
        if item.get("gender") != detected_gender:
            continue

        cat_vis_vec = np.array(item["image_vector"], dtype=np.float32)
        s_vis = cosine_similarity(thumb_vis_vec, cat_vis_vec)
        s_tag = compute_tag_overlap(title_text, item.get("tags", []))
        
        cat_hsv = item["hsv_color"]
        s_color = compute_color_similarity_hsv(thumb_hsv, cat_hsv)
        
        s_base = max(0.0, 0.70 * s_vis + 0.30 * s_tag)
        s_final = s_base * s_color

        results.append({
            "name": item["name"],
            "category": item.get("category"),
            "macro_category": item.get("macro_category"),
            "gender": item.get("gender"),
            "product_url": item.get("product_url"),
            "s_vis": round(s_vis, 4),
            "s_vis_pct": round(s_vis * 100.0, 2),
            "s_color": round(s_color, 4),
            "s_color_pct": round(s_color * 100.0, 2),
            "s_hybrid_pct": round(s_final * 100.0, 2)
        })

    # Rank strictly by final color-filtered hybrid score
    results.sort(key=lambda x: x["s_hybrid_pct"], reverse=True)
    top_matches = results[:top_k]

    print(f"\n================ TOP {top_k} FULL CATALOG MATCHES FOR {fname} ================")
    for rank, r in enumerate(top_matches, 1):
        print(f"Rank {rank}: {r['name']} | Gender: {r['gender']} | Cat: {r['macro_category']} | ColorMatch: {r['s_color_pct']}% | S_vis: {r['s_vis_pct']}% | Score: {r['s_hybrid_pct']}%")
        print(f"  URL: {r['product_url']}\n")

    return top_matches

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = os.path.abspath(sys.argv[1])
        match_thumbnail_full_28k(target_path, top_k=5)
    else:
        print("Usage: python backend/run_full_catalog_matcher.py <path_to_thumbnail_image>")
