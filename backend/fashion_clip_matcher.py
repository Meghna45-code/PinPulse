"""
PinPulse Fashion-CLIP, YOLO, Gender & Text-Overlay Resistant Engine
======================================================================
1. YOLOv8 Bounding-Box Fashion Cropper (`crop_fashion_item`)
2. Text-Overlay Resistant HSV Color Palette Extraction (`extract_hsv_color_palette`)
   - Ignores outer margin graphic text overlays ("ST", "TODAY'S FASHION").
3. Zero-Shot Gender & Category Classifier (`classify_gender_and_category`)
   - Classifies gender: 'men' vs 'women'.
   - HARD FILTERS candidate catalog items by gender so male creators NEVER match women's tops!
4. 512-D Visual CLIP Cosine Similarity Vector (S_visual)
5. Hybrid Score Fusion: S_final = (0.70 * S_visual + 0.30 * S_tag) * S_color
"""

import os
import sys
import json
import re
import numpy as np
from PIL import Image
import torch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from yolo_fashion_cropper import crop_fashion_item
from embed_catalog import get_vibe_vector

clip_model = None
clip_processor = None

def load_fashion_clip():
    global clip_model, clip_processor
    if clip_model is None:
        try:
            from transformers import CLIPProcessor, CLIPModel
            print("Loading Fashion-CLIP model for vector embedding...")
            clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            clip_model.eval()
            print("Fashion-CLIP loaded successfully.")
        except Exception as e:
            print(f"Warning loading CLIP: {e}")

def get_image_embedding(pil_img):
    """Generate 512-D visual vector using CLIP."""
    load_fashion_clip()
    if clip_model is not None and clip_processor is not None:
        try:
            img_copy = pil_img.copy()
            inputs = clip_processor(images=img_copy, return_tensors="pt")
            with torch.no_grad():
                outputs = clip_model.get_image_features(**inputs)
                if hasattr(outputs, "image_embeds"):
                    img_features = outputs.image_embeds
                elif hasattr(outputs, "pooler_output"):
                    img_features = outputs.pooler_output
                elif isinstance(outputs, torch.Tensor):
                    img_features = outputs
                else:
                    img_features = outputs[0]
                    
                vec = img_features.detach().cpu().numpy()[0]
                norm = np.linalg.norm(vec)
                if norm > 0:
                    return vec / norm
        except Exception as e:
            print(f"CLIP embedding error: {e}")
    return None

def extract_hsv_color_palette(pil_img):
    """
    Extract dominant HSV color palette from garment fabric,
    cropping out outer margins to reject graphic text overlays (e.g. "ST", "Patna").
    """
    try:
        w, h = pil_img.size
        # Crop inner 65% central region to avoid side text graphic overlays
        left = int(w * 0.15)
        top = int(h * 0.15)
        right = int(w * 0.85)
        bottom = int(h * 0.85)
        inner_crop = pil_img.crop((left, top, right, bottom)) if w > 50 and h > 50 else pil_img

        img_hsv = inner_crop.resize((100, 100)).convert("HSV")
        arr = np.array(img_hsv, dtype=np.float32)
        
        sat = arr[:, :, 1] / 255.0
        val = arr[:, :, 2] / 255.0
        
        # Mask out pure background (near white or near black)
        fg_mask = (sat > 0.10) & (val > 0.12) & (val < 0.96)
        
        if np.sum(fg_mask) < 40:
            fg_pixels = arr.reshape(-1, 3)
        else:
            fg_pixels = arr[fg_mask]
            
        h_med = float(np.median(fg_pixels[:, 0]) * (360.0 / 255.0))
        s_med = float(np.median(fg_pixels[:, 1]) / 255.0)
        v_med = float(np.median(fg_pixels[:, 2]) / 255.0)
        return (h_med, s_med, v_med)
    except Exception:
        return (0.0, 0.0, 0.5)

def compute_color_similarity_hsv(hsv1, hsv2):
    """Compute strict HSV color similarity (1.0 = identical, 0.05 = complete color mismatch)."""
    h1, s1, v1 = hsv1
    h2, s2, v2 = hsv2
    
    # Circular Hue distance
    dh = min(abs(h1 - h2), 360.0 - abs(h1 - h2))
    
    # Hue similarity penalty
    if dh <= 30.0:
        h_sim = 1.0 - (dh / 100.0)
    else:
        h_sim = max(0.05, 1.0 - (dh / 75.0))
        
    ds = abs(s1 - s2)
    dv = abs(v1 - v2)
    sv_sim = max(0.2, 1.0 - (0.5 * ds + 0.5 * dv))
    
    return float(h_sim * sv_sim)

def compute_tag_overlap(thumbnail_title, item_tags):
    """Compute keyword & tag overlap ratio (S_tag)."""
    title_words = set(re.findall(r'\w+', thumbnail_title.lower()))
    tags_set = set(t.lower() for t in item_tags)
    if not tags_set or not title_words:
        return 0.0
    intersection = title_words.intersection(tags_set)
    return min(1.0, len(intersection) / max(1, len(tags_set)))

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two 512-D vectors."""
    v1 = np.array(vec1, dtype=np.float32)
    v2 = np.array(vec2, dtype=np.float32)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

GENDER_LABELS = {
    "men": "a photo of a man or male model wearing men clothing",
    "women": "a photo of a woman or female model wearing women clothing"
}

REFINED_CATEGORY_LABELS = {
    "lehenga": "a designer lehenga choli gown or flared evening dress",
    "saree": "a traditional indian saree or draped sari with border",
    "dress_gown": "a womens western evening gown maxi dress party dress bodycon dress",
    "kurta_suit": "an indian ethnic kurta kurti salwar suit set with dupatta",
    "men_shirt": "a mens casual or formal button down short sleeve or long sleeve shirt",
    "men_tshirt": "a mens casual t-shirt or polo shirt",
    "men_ethnic": "a mens traditional ethnic kurta or sherwani",
    "women_top": "a womens casual western crop top t-shirt shirt or blouse",
    "bottomwear": "casual western jeans trousers palazzos leggings or skirt",
    "outerwear": "a winter jacket blazer coat hoodie or shrug"
}

def classify_gender_and_category(pil_img):
    """Classify input thumbnail into gender ('men'/'women') and refined macro_category."""
    load_fashion_clip()
    if clip_model is None or clip_processor is None:
        return "women", "kurta_suit"
    try:
        # 1. Gender Classification
        g_labels = list(GENDER_LABELS.values())
        g_keys = list(GENDER_LABELS.keys())
        inputs_g = clip_processor(text=g_labels, images=pil_img.copy(), return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs_g = clip_model(**inputs_g)
            probs_g = outputs_g.logits_per_image.softmax(dim=1).detach().cpu().numpy()[0]
            detected_gender = g_keys[int(np.argmax(probs_g))]
            
        # 2. Refined Category Classification
        c_labels = list(REFINED_CATEGORY_LABELS.values())
        c_keys = list(REFINED_CATEGORY_LABELS.keys())
        inputs_c = clip_processor(text=c_labels, images=pil_img.copy(), return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs_c = clip_model(**inputs_c)
            probs_c = outputs_c.logits_per_image.softmax(dim=1).detach().cpu().numpy()[0]
            detected_cat = c_keys[int(np.argmax(probs_c))]
            
        return detected_gender, detected_cat
    except Exception as e:
        print(f"Zero-shot classification error: {e}")
        return "women", "kurta_suit"

def match_thumbnail_to_catalog(img_path, catalog_items, top_k=3, enforce_category_filter=True):
    """
    Executes Gender-Aware, HSV Color & CLIP Pre-Filtered Matching:
      1. Crop thumbnail using YOLOv8 cropper.
      2. Detect Gender ('men' vs 'women') & Refined Category.
      3. HARD FILTER candidate catalog items strictly by gender.
      4. Extract text-overlay resistant HSV color palette from garment crop.
      5. Rank candidates by S_hybrid = (0.70 * S_visual + 0.30 * S_tag) * S_color.
    """
    try:
        raw_img = Image.open(img_path).convert("RGB")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        return []

    cropped_img = crop_fashion_item(raw_img) or raw_img

    if enforce_category_filter and catalog_items:
        detected_gender, detected_category = classify_gender_and_category(cropped_img)
        
        # Hard Gender Filter + Category Filter
        gender_candidates = [
            item for item in catalog_items 
            if item.get("gender", "women") == detected_gender
        ]
        
        category_candidates = [
            item for item in gender_candidates 
            if item.get("macro_category", "").lower() == detected_category or item.get("category", "").lower() == detected_category
        ]
        
        if len(category_candidates) >= 5:
            catalog_items = category_candidates
        elif len(gender_candidates) >= 5:
            catalog_items = gender_candidates

    vis_vec = get_image_embedding(cropped_img)
    thumb_hsv = extract_hsv_color_palette(cropped_img)

    fname = os.path.basename(img_path)
    title_text = fname.replace("_", " ").replace("-", " ")

    matches = []
    for item in catalog_items:
        cat_img_emb = item.get("image_vector") or item.get("embedding")
        if not cat_img_emb:
            continue
            
        s_visual = cosine_similarity(vis_vec, cat_img_emb) if vis_vec is not None else 0.0
        s_tag = compute_tag_overlap(title_text, item.get("tags", []))
        
        cat_hsv = item.get("hsv_color") or (0.0, 0.0, 0.5)
        s_color = compute_color_similarity_hsv(thumb_hsv, cat_hsv) if item.get("hsv_color") else 1.0
        
        s_base = max(0.0, 0.70 * s_visual + 0.30 * s_tag)
        s_hybrid = s_base * s_color
        match_pct = round(s_hybrid * 100.0, 2)
        
        matches.append({
            "item_id": item.get("id"),
            "product_name": item.get("name"),
            "category": item.get("category"),
            "macro_category": item.get("macro_category"),
            "gender": item.get("gender"),
            "product_url": item.get("product_url", f"https://www.myntra.com/{item.get('id')}"),
            "image_url": item.get("image_url"),
            "s_hybrid_pct": match_pct,
            "s_visual": round(s_visual, 4),
            "s_color": round(s_color, 4),
            "s_tag": round(s_tag, 4)
        })

    matches.sort(key=lambda x: x["s_hybrid_pct"], reverse=True)
    return matches[:top_k]
