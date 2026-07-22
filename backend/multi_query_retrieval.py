"""
PinPulse Multi-Query Retrieval  (OFFLINE SEEDER ONLY)
======================================================
Provides three independent query paths for catalog matching:

  Path 1 — Transcript → Gemini → dress_vector  (existing)
  Path 2 — YouTube thumbnail → CLIP zero-shot → garment tags → dress_vector (NEW)
  Path 3 — Regional prior (pincode) → vibe_vector               (NEW fallback)

All three ranked candidate lists are fused with Reciprocal Rank Fusion (RRF).
CLIP model is loaded lazily and only used here — never in the live API path.

RRF formula: score(item) = Σ  1 / (k + rank_in_list)   [k=60 by default]
"""

import os
import io
import json
import logging
import numpy as np
import requests
from typing import Optional

logger = logging.getLogger("multi_query_retrieval")

# ── CLIP vocab for zero-shot thumbnail classification ─────────────────────────
# Each label is a complete, unambiguous phrase — no color-garment binding risk.
# Three tiers: garment type, color descriptor, vibe phrase (compound OK).

GARMENT_LABELS = [
    "a saree",
    "a kurta",
    "a salwar suit",
    "a lehenga",
    "a sherwani",
    "a kurti",
    "a dupatta",
    "a mundu",
    "a hoodie",
    "a denim jacket",
    "a shirt",
    "a t-shirt",
    "a dress",
    "a blazer",
    "cargo trousers",
    "a winter jacket",
    "a shawl",
]

COLOR_LABELS = [
    "saffron yellow clothing",
    "red clothing",
    "maroon clothing",
    "white clothing",
    "cream colored clothing",
    "golden clothing",
    "blue clothing",
    "green clothing",
    "black clothing",
    "pink clothing",
    "pastel clothing",
    "multicolor clothing",
]

VIBE_LABELS = [
    "traditional Indian festive attire",
    "ethnic traditional wear",
    "handloom saree",
    "bridal wear",
    "casual streetwear outfit",
    "summer casual clothing",
    "winter warm clothing",
    "coastal relaxed outfit",
    "earthy handloom artisan fashion",
    "indo-western fusion outfit",
]

ALL_LABELS = GARMENT_LABELS + COLOR_LABELS + VIBE_LABELS

# Confidence threshold — labels below this are ignored
CLIP_CONFIDENCE_THRESHOLD = 0.15

# Mapping from CLIP garment label → embed_dress compatible tags
_LABEL_TO_TAGS = {
    "a saree":               ["saree", "ethnic", "traditional"],
    "a kurta":               ["kurta", "ethnic"],
    "a salwar suit":         ["suit", "salwar", "ethnic", "casual"],
    "a lehenga":             ["lehenga", "ethnic", "festive", "ceremonial"],
    "a sherwani":            ["sherwani", "ethnic", "festive", "men", "ceremonial"],
    "a kurti":               ["kurti", "ethnic", "casual", "dailywear"],
    "a dupatta":             ["dupatta", "ethnic"],
    "a mundu":               ["mundu", "ethnic", "traditional"],
    "a hoodie":              ["hoodie", "streetwear", "casual", "modern"],
    "a denim jacket":        ["jacket", "denim", "streetwear", "modern"],
    "a shirt":               ["shirt", "casual"],
    "a t-shirt":             ["tee", "casual", "cotton"],
    "a dress":               ["dress", "casual"],
    "a blazer":              ["blazer", "formal", "smart_casual"],
    "cargo trousers":        ["cargo", "streetwear", "modern"],
    "a winter jacket":       ["jacket", "winter", "warm", "heavy-weight"],
    "a shawl":               ["shawl", "winter", "ethnic"],
    # colour labels → colour tags
    "saffron yellow clothing": ["saffron", "yellow"],
    "red clothing":            ["red"],
    "maroon clothing":         ["maroon"],
    "white clothing":          ["white"],
    "cream colored clothing":  ["cream", "off-white"],
    "golden clothing":         ["gold", "zari"],
    "blue clothing":           ["blue"],
    "green clothing":          ["green"],
    "black clothing":          ["black"],
    "pink clothing":           ["pink"],
    "pastel clothing":         ["pastel"],
    "multicolor clothing":     ["vibrant", "multicolor"],
    # vibe labels → style tags
    "traditional Indian festive attire": ["ethnic", "festive", "traditional", "ceremonial"],
    "ethnic traditional wear":           ["ethnic", "traditional"],
    "handloom saree":                    ["saree", "handloom", "ethnic", "traditional"],
    "bridal wear":                       ["ceremonial", "bridal", "festive", "heavy_silk"],
    "casual streetwear outfit":          ["streetwear", "casual", "modern"],
    "summer casual clothing":            ["casual", "summer", "cotton", "breathable"],
    "winter warm clothing":              ["winter", "warm", "heavy-weight"],
    "coastal relaxed outfit":            ["coastal", "linen", "summer", "breathable"],
    "earthy handloom artisan fashion":   ["handloom", "artisanal", "earthy", "boho"],
    "indo-western fusion outfit":        ["fusion", "indo-western", "modern", "contemporary_fusion"],
}

# ── Lazy CLIP model loader ────────────────────────────────────────────────────
_clip_model = None
_clip_processor = None
_clip_backend = None  # "torch" | "gemini" | None


def _load_clip():
    """
    Try to load the CLIP torch model. If torch is not installed, set backend to
    'gemini' so classify_thumbnail_with_clip() falls over to Gemini Vision.
    """
    global _clip_model, _clip_processor, _clip_backend
    if _clip_backend is not None:
        return _clip_model, _clip_processor

    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        logger.info("[CLIP] Loading openai/clip-vit-base-patch32 (first use)…")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model.eval()
        _clip_backend = "torch"
        logger.info("[CLIP] Torch model loaded — using CLIP backend.")
    except ImportError:
        logger.info("[CLIP] torch not installed — switching to Gemini Vision backend.")
        _clip_backend = "gemini"
    except Exception as e:
        logger.error(f"[CLIP] Failed to load model: {e} — switching to Gemini Vision backend.")
        _clip_backend = "gemini"

    return _clip_model, _clip_processor


# ── Thumbnail fetching ─────────────────────────────────────────────────────────

def _fetch_thumbnail_bytes(video_id: str):
    """
    Fetch raw thumbnail bytes. Tries 4 YouTube resolutions, returns (bytes, url) or (None, None).
    """
    urls = [
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/0.jpg",
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code == 200 and len(resp.content) > 5000:
                return resp.content, url
        except Exception:
            continue
    return None, None


def _fetch_thumbnail_pil(video_id: str):
    """Return PIL.Image or None."""
    from PIL import Image
    raw, _ = _fetch_thumbnail_bytes(video_id)
    if raw is None:
        return None
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return None


# ── Gemini Vision fallback classifier ─────────────────────────────────────────
# Used when torch/CLIP is unavailable. Sends the thumbnail to Gemini and asks
# it to identify the garment type, colour, and style — same output schema as CLIP.

_GEMINI_VISION_PROMPT = """You are a fashion expert. Analyze this clothing thumbnail image.
Identify the MAIN garment visible. Return ONLY valid JSON, no markdown:
{
  "item": "<garment name e.g. 'red silk saree'>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"],
  "aesthetic": "<style e.g. 'traditional ethnic' or 'casual streetwear'>",
  "color": "<primary color>",
  "material": "<fabric if visible, else empty string>",
  "fabric": "<fabric if visible, else empty string>",
  "age_group": "",
  "estimated_price_inr": null,
  "occasion": "<festive/casual/wedding/streetwear>",
  "_source": "gemini_vision"
}
Tags must be from: saree, kurta, lehenga, sherwani, kurti, hoodie, jacket, shirt, t-shirt,
ethnic, festive, traditional, casual, streetwear, handloom, silk, cotton, linen, gold, red,
yellow, saffron, white, cream, maroon, blue, green, black, pink, pastel, ceremonial, bridal."""

def _classify_thumbnail_gemini(video_id: str) -> Optional[dict]:
    """Use Gemini Vision to classify thumbnail when torch is unavailable."""
    import time
    raw, url = _fetch_thumbnail_bytes(video_id)
    if raw is None:
        logger.warning(f"[GeminiVision] No thumbnail for {video_id}")
        return None

    try:
        import google.generativeai as genai
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("[GeminiVision] No GEMINI_API_KEY set")
            return None
        genai.configure(api_key=api_key)
        # Use gemini-flash-lite to share the same quota pool as text extraction
        # and stay well under per-minute token limits.
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")

        import PIL.Image
        img = PIL.Image.open(io.BytesIO(raw)).convert("RGB")

        # Small pause so thumbnail call doesn't immediately stack on top of
        # the text extraction call that just finished for this video.
        time.sleep(2)

        def _call_with_retry(max_retries=2):
            for attempt in range(max_retries + 1):
                try:
                    return model.generate_content([_GEMINI_VISION_PROMPT, img])
                except Exception as exc:
                    msg = str(exc)
                    if "429" in msg:
                        # Extract retry delay suggested by API (default 12s)
                        import re
                        m = re.search(r'retry in (\d+)', msg)
                        wait = int(m.group(1)) + 2 if m else 12
                        if attempt < max_retries:
                            logger.info(f"[GeminiVision] 429 for {video_id}, waiting {wait}s (attempt {attempt+1}/{max_retries})")
                            time.sleep(wait)
                        else:
                            raise
                    else:
                        raise

        response = _call_with_retry()
        text = response.text.strip()

        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()

        result = json.loads(text)
        # Ensure required keys exist with safe defaults
        result.setdefault("tags", [])
        result.setdefault("aesthetic", "casual")
        result.setdefault("color", "")
        result.setdefault("material", "")
        result.setdefault("fabric", "")
        result.setdefault("age_group", "")
        result.setdefault("estimated_price_inr", None)
        result.setdefault("occasion", "")
        result["_source"] = "gemini_vision"
        logger.info(f"[GeminiVision] {video_id} → '{result.get('item')}' tags={result.get('tags')[:3]}")
        return result

    except Exception as e:
        logger.error(f"[GeminiVision] Classification failed for {video_id}: {e}")
        return None


# ── Core thumbnail classifier — dispatches to CLIP or Gemini Vision ───────────

def classify_thumbnail_with_clip(video_id: str) -> Optional[dict]:
    """
    Classify the YouTube thumbnail for video_id into a dress_meta dict.

    Backend selection (automatic):
      • torch installed → openai/clip-vit-base-patch32 zero-shot scoring
      • torch missing   → Gemini Vision API (same output schema)

    Returns a dress_meta dict compatible with embed_dress(), or None on failure.
    """
    _load_clip()  # Determines backend on first call

    if _clip_backend == "gemini":
        return _classify_thumbnail_gemini(video_id)

    # ── torch CLIP path ───────────────────────────────────────────────────────
    img = _fetch_thumbnail_pil(video_id)
    if img is None:
        logger.warning(f"[CLIP] No thumbnail available for {video_id}")
        return None

    try:
        import torch
        inputs = _clip_processor(
            images=img,
            text=ALL_LABELS,
            return_tensors="pt",
            padding=True,
            truncation=True,
        )
        with torch.no_grad():
            outputs = _clip_model(**inputs)
            logits = outputs.logits_per_image[0]
            probs = logits.softmax(dim=0).cpu().numpy()

        scored = sorted(zip(ALL_LABELS, probs.tolist()), key=lambda x: -x[1])
        logger.info(f"[CLIP] {video_id} top-5: {[(l, round(p, 3)) for l, p in scored[:5]]}")

        accepted = [(label, prob) for label, prob in scored if prob >= CLIP_CONFIDENCE_THRESHOLD]
        if not accepted:
            return None

        garment_hits = [(l, p) for l, p in accepted if l in GARMENT_LABELS]
        color_hits   = [(l, p) for l, p in accepted if l in COLOR_LABELS]
        vibe_hits    = [(l, p) for l, p in accepted if l in VIBE_LABELS]

        all_tags = []
        top_garment = garment_hits[0][0] if garment_hits else None
        top_color   = color_hits[0][0]   if color_hits   else None
        top_vibe    = vibe_hits[0][0]    if vibe_hits    else None

        for label, _ in (garment_hits + vibe_hits + color_hits)[:6]:
            all_tags.extend(_LABEL_TO_TAGS.get(label, []))

        seen = set()
        deduped_tags = [t for t in all_tags if not (t in seen or seen.add(t))]

        item_name = top_garment.lstrip("a ").strip() if top_garment else "outfit"
        color_str = ""
        if top_color:
            color_str = top_color.replace(" clothing", "").strip()
            item_name = f"{color_str} {item_name}"

        aesthetic_parts = []
        if top_vibe:
            aesthetic_parts.append(top_vibe.replace(" outfit", "").replace(" attire", ""))
        elif any(t in deduped_tags for t in ["ethnic", "festive", "traditional"]):
            aesthetic_parts.append("traditional ethnic")
        elif any(t in deduped_tags for t in ["streetwear", "modern"]):
            aesthetic_parts.append("casual streetwear")
        aesthetic = " ".join(aesthetic_parts) or "casual"

        return {
            "item":                item_name,
            "description":         f"Thumbnail-classified garment: {item_name}. Detected via CLIP.",
            "tags":                deduped_tags,
            "aesthetic":           aesthetic,
            "material":            "",
            "fabric":              "",
            "color":               color_str,
            "age_group":           "",
            "estimated_price_inr": None,
            "occasion":            "",
            "_source":             "clip_thumbnail",
        }

    except Exception as e:
        logger.error(f"[CLIP] Classification failed for {video_id}: {e}")
        return None


# ── Candidate list builder ─────────────────────────────────────────────────────

def build_candidate_list(dress_vector: list, catalog: list, zip_code: str, top_k: int = 20):
    """
    Returns top_k catalog items sorted by cosine similarity for one query vector.
    Respects zip_code scoping (same logic as find_best_catalog_match).

    Returns: list of (product_dict, cosine_score) tuples, best-first.
    """
    scored = []
    for p in catalog:
        p_zips = p.get("zip_codes", [])
        if p_zips and zip_code not in p_zips:
            continue
        p_emb = p.get("embedding", [])
        if not p_emb or len(p_emb) != len(dress_vector):
            continue
        a = np.array(dress_vector, dtype=float)
        b = np.array(p_emb, dtype=float)
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na == 0 or nb == 0:
            continue
        cos = float(np.dot(a, b) / (na * nb))
        scored.append((p, cos))

    scored.sort(key=lambda x: -x[1])
    return scored[:top_k]


# ── Reciprocal Rank Fusion ─────────────────────────────────────────────────────

def reciprocal_rank_fusion(ranked_lists: list, k: int = 60) -> list:
    """
    Standard RRF over multiple ranked lists.

    Args:
        ranked_lists: list of lists, each containing (product_dict, score) tuples
                      sorted best-first. Each list corresponds to one query path.
        k: smoothing constant (default 60 per Cormack et al.)

    Returns:
        List of (product_dict, rrf_score) sorted by rrf_score descending.
    """
    rrf_scores: dict = {}   # product_id → cumulative rrf score
    product_map: dict = {}  # product_id → product_dict (keep first seen)

    for ranked in ranked_lists:
        for rank_idx, (product, _cos_score) in enumerate(ranked):
            p_id = product.get("id")
            if p_id is None:
                continue
            contribution = 1.0 / (k + rank_idx + 1)  # rank is 0-indexed
            rrf_scores[p_id] = rrf_scores.get(p_id, 0.0) + contribution
            if p_id not in product_map:
                product_map[p_id] = product

    fused = sorted(
        [(product_map[pid], score) for pid, score in rrf_scores.items()],
        key=lambda x: -x[1],
    )
    return fused


# ── Regional prior builder ─────────────────────────────────────────────────────

_REGION_PRIORS = {
    "800008": {
        "tags": ["ethnic", "festive", "silk", "traditional", "kurta", "saree", "chhath", "banarasi"],
        "aesthetic": "traditional ethnic Bihar",
    },
    "682001": {
        "tags": ["ethnic", "kasavu_weave", "traditional", "saree", "mundu", "white", "cream", "gold"],
        "aesthetic": "traditional Kerala ethnic",
    },
    "752001": {
        "tags": ["ethnic", "sambalpuri", "handloom", "ikat", "traditional", "silk", "saree"],
        "aesthetic": "earthy handloom artisan Odisha",
    },
}


def build_regional_prior_vector(pincode: str) -> list:
    """
    Returns a 512-dim vibe vector for the region's baseline fashion style.
    Used as Query Path 3 when no transcript and no thumbnail available.
    """
    import sys
    sys.path.append(os.path.dirname(__file__))
    from embed_catalog import get_vibe_vector

    prior = _REGION_PRIORS.get(pincode, {
        "tags": ["ethnic", "casual", "traditional"],
        "aesthetic": "casual Indian",
    })
    return get_vibe_vector(prior["tags"], category_str="festive", aesthetic_str=prior["aesthetic"])


# ── Main orchestrator ──────────────────────────────────────────────────────────

def find_best_match_multi_query(
    video_id: str,
    transcript_dresses: list,
    catalog: list,
    zip_code: str,
    top_k: int = 20,
    rrf_k: int = 60,
) -> tuple:
    """
    Multi-query retrieval with RRF fusion.

    Args:
        video_id:          YouTube video ID (for thumbnail fetch)
        transcript_dresses: list of dress_meta dicts from Gemini (may be empty)
        catalog:           list of product dicts with 'embedding' field
        zip_code:          user ZIP code for scoping
        top_k:             candidates per query to pass into RRF
        rrf_k:             RRF smoothing constant

    Returns:
        (best_product, rrf_score, query_sources_used)
        where query_sources_used is a list of strings describing which paths contributed.
    """
    import sys
    sys.path.append(os.path.dirname(__file__))
    from embed_catalog import get_vibe_vector

    all_ranked_lists = []
    query_sources = []

    # ── Path 1: Transcript → Gemini → dress_vector ────────────────────────────
    if transcript_dresses:
        for dress in transcript_dresses:
            from run_transcript_seeder import embed_dress
            vec = embed_dress(dress)
            candidates = build_candidate_list(vec, catalog, zip_code, top_k=top_k)
            if candidates:
                all_ranked_lists.append(candidates)
        if all_ranked_lists:
            query_sources.append("transcript_gemini")

    # ── Path 2: Thumbnail → CLIP zero-shot ────────────────────────────────────
    clip_result = classify_thumbnail_with_clip(video_id)
    if clip_result:
        from run_transcript_seeder import embed_dress
        clip_vec = embed_dress(clip_result)
        clip_candidates = build_candidate_list(clip_vec, catalog, zip_code, top_k=top_k)
        if clip_candidates:
            all_ranked_lists.append(clip_candidates)
            query_sources.append("clip_thumbnail")
    else:
        logger.info(f"[RRF] No CLIP signal for {video_id}, skipping Path 2.")

    # ── Path 3: Regional prior (always available as safety net) ───────────────
    prior_vec = build_regional_prior_vector(zip_code)
    prior_candidates = build_candidate_list(prior_vec, catalog, zip_code, top_k=top_k)
    if prior_candidates:
        all_ranked_lists.append(prior_candidates)
        query_sources.append("regional_prior")

    # ── No usable paths at all — shouldn't happen but guard anyway ────────────
    if not all_ranked_lists:
        logger.warning(f"[RRF] No query paths produced results for {video_id}")
        return None, 0.0, []

    # ── Fuse with RRF ─────────────────────────────────────────────────────────
    fused = reciprocal_rank_fusion(all_ranked_lists, k=rrf_k)

    if not fused:
        return None, 0.0, query_sources

    best_product, best_rrf_score = fused[0]
    logger.info(
        f"[RRF] {video_id} → '{best_product.get('name')}' "
        f"(rrf={best_rrf_score:.4f}, sources={query_sources})"
    )
    return best_product, best_rrf_score, query_sources
