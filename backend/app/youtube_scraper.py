import os
import json
import logging
from typing import Dict, Any, List

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

logger = logging.getLogger("youtube_scraper")

# ─────────────────────────────────────────────────────────────────────────────
# Curated 10-video creator feed per ZIP cluster
# All video IDs verified as working Indian fashion/lifestyle content
# ─────────────────────────────────────────────────────────────────────────────
ZIP_CREATOR_VIDEOS = {
    "800008": [
        {
            "video_id": "U_nkHYPc1ww",
            "title": "Fabric market in Patna | Patna market #fabricmarket #fabric #desginer #patnavlogs #patnamarket",
            "channel": "Pratibha Shree",
            "thumbnail_url": "https://i.ytimg.com/vi/U_nkHYPc1ww/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/U_nkHYPc1ww",
            "llm_extracted_description": "Garments featured: saffron yellow Chhath Puja silk kurta set, Bhagalpuri tussar silk saree with Madhubani hand-paint, royal blue embroidered wedding sherwani",
            "inferred_tags": [
                "wedding", "traditional", "ethnic", "kurta", "madhubani", "bhagalpuri", "silk", "tussar", "menswear", "festive", "sherwani"
            ]
        },
        {
            "video_id": "FqilEHTE5BA",
            "title": "ZUDIO summer collection #summer #zudio #zudioshoppingvlog #summerfashion #shopping #shoppingvlog",
            "channel": "HER Wardrobe",
            "thumbnail_url": "https://i.ytimg.com/vi/FqilEHTE5BA/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/FqilEHTE5BA",
            "llm_extracted_description": "Vibrant Bhagalpuri tussar silk kurta featuring traditional Madhubani hand-painted motifs on the neckline, perfect for Chhath Puja festivities. Regal ivory dupion silk sherwani with subtle thread work ",
            "inferred_tags": [
                "groom", "wedding", "chhath", "kurtas", "casual", "dailywear", "cotton", "ethnic", "madhubani", "bhagalpuri", "silk", "festive", "sherwani"
            ]
        },
        {
            "video_id": "55apryEpLEs",
            "title": "Khetan Market patna #khetanmarket #patna #patnamarket #trending #lahenga #festivewear #ad #bihar",
            "channel": "Asmita",
            "thumbnail_url": "https://i.ytimg.com/vi/55apryEpLEs/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/55apryEpLEs",
            "llm_extracted_description": "Vibrant saffron-colored pure cotton kurta paired with a white churidar, specifically styled for Chhath Puja festivities and morning rituals along the ghats. Elegant textured Bhagalpuri tussar silk jac",
            "inferred_tags": [
                "wedding", "chhath", "bandhgala", "nehru jacket", "traditional", "cotton", "ethnic", "kurta", "madhubani", "bhagalpuri", "silk", "art", "festive", "fusion"
            ]
        }
    ],
    "682001": [
        {
            "video_id": "J_F2dzbUXvg",
            "title": "Pinterest store at Edappally #fashion #boutique #clothing #ytshorts",
            "channel": "VIOLET STORE",
            "thumbnail_url": "https://i.ytimg.com/vi/J_F2dzbUXvg/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/J_F2dzbUXvg",
            "llm_extracted_description": "Authentic Kerala cotton-mix handloom saree featuring a rich tissue gold zari brocade pallu and traditional border, perfect for Onam and Vishu celebrations. Contemporary breathable cotton-linen short k",
            "inferred_tags": [
                "gold zari", "vishu", "summer wear", "pastel dress", "linen", "kerala fashion", "mundu", "boho chic", "daywear", "kasavu", "onam", "traditional", "ethnic", "cotton linen", "block print", "menswear", "kerala saree", "casual ethnic"
            ]
        },
        {
            "video_id": "mZPnF5dMzcM",
            "title": "Stylish Finds at Westernish Kochi! Trendy Tops, Jeans, & More | Kochi  #fashion #shopping",
            "channel": "Deals Kochi",
            "thumbnail_url": "https://i.ytimg.com/vi/mZPnF5dMzcM/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/mZPnF5dMzcM",
            "llm_extracted_description": "Handloom cream-colored cotton Kasavu saree featuring a rich, authentic pure gold zari brocade pallu and a classic green and gold temple border, perfect for Vishu and Onam celebrations. Classic white d",
            "inferred_tags": [
                "pastel", "vishu", "linen", "kerala-wear", "mundu", "veshti", "set-saree", "summer-wear", "kasavu", "traditional", "kerala-sarees", "casual", "coastal", "maxi-dress", "handloom", "block-print", "festive", "mens-ethnic"
            ]
        },
        {
            "video_id": "Vh7B2k8-CLc",
            "title": "UNDER 500/- FASHIONABLE CLOTHES #kochi #affordableshopping #youtubeshorts #youtube",
            "channel": "KOCHI TOPICS",
            "thumbnail_url": "https://i.ytimg.com/vi/Vh7B2k8-CLc/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/Vh7B2k8-CLc",
            "llm_extracted_description": "Authentic Kerala cotton handloom saree featuring a pristine off-white body and a rich, traditional real-zari brocade pallu and border, perfect for Onam and Vishu celebrations. Classic white Kerala cot",
            "inferred_tags": [
                "pastel", "zari", "summerwear", "mensethnic", "keralamundu", "mundu", "casual", "keralasaree", "dailywear", "kasavu", "traditional", "onam", "linendress", "coastal", "vishuwear", "handloom", "sustainable", "festive"
            ]
        }
    ],
    "752001": [
        {
            "video_id": "erCRv3qln1Q",
            "title": "Bapa Pua Renuka Dress Shop,📍CUTTACK",
            "channel": "Payalvlogs",
            "thumbnail_url": "https://i.ytimg.com/vi/erCRv3qln1Q/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/erCRv3qln1Q",
            "llm_extracted_description": "Handwoven maroon and black Sambalpuri silk saree featuring traditional Pasapali (chessboard) ikat motifs and intricate temple border, highlighting Odisha's rich textile heritage. Vibrant yellow cotton",
            "inferred_tags": [
                "rudraksha", "odisha", "bomkai", "applique", "handicraft", "kurtas", "sambalpuri", "ikat", "traditional", "cotton", "handloom", "silk", "pipli", "festive", "summer"
            ]
        },
        {
            "video_id": "rmZXaeTxjDg",
            "title": "Cuttack best Kurti set shop for all sizes| #cuttacktop10",
            "channel": "CuttackTop 10",
            "thumbnail_url": "https://i.ytimg.com/vi/rmZXaeTxjDg/hqdefault.jpg",
            "video_url": "https://youtube.com/shorts/rmZXaeTxjDg",
            "llm_extracted_description": "Authentic crimson and black handloom Sambalpuri silk saree featuring traditional shankha (conch), chakra (wheel), and phula (flower) motifs woven with intricate tie-dye precision, representing the ric",
            "inferred_tags": [
                "odisha", "festive", "applique", "handicraft", "odisha weave", "sambalpuri", "embroidary", "kumbha", "ikat", "traditional", "ethnic", "cotton", "handloom", "silk", "tussar", "pipli", "temple border", "casual ethnic"
            ]
        }
    ]
}


MOCK_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pinpulse_mock_db.json"))
METADATA_CACHE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "youtube_metadata_cache.json"))

def get_youtube_video_metadata(video_id: str) -> Dict[str, str]:
    cache = {}
    if os.path.exists(METADATA_CACHE_FILE):
        try:
            with open(METADATA_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load video metadata cache: {e}")

    if video_id in cache:
        return cache[video_id]

    logger.info(f"Fetching oEmbed metadata for video: {video_id}")
    try:
        import requests
        r = requests.get(f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}", timeout=5)
        if r.status_code == 200:
            res = r.json()
            if "error" not in res:
                meta = {
                    "title": res.get("title", f"Fashion Trend Vlog - {video_id}"),
                    "channel": res.get("author_name", "Fashion Creator"),
                    "thumbnail_url": res.get("thumbnail_url", f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg")
                }
                cache[video_id] = meta
                try:
                    with open(METADATA_CACHE_FILE, "w", encoding="utf-8") as f:
                        json.dump(cache, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.warning(f"Failed to save video metadata cache: {e}")
                return meta
    except Exception as e:
        logger.warning(f"Failed to fetch oEmbed metadata for {video_id}: {e}")

    return {
        "title": f"Fashion Trend Vlog - {video_id}",
        "channel": "Fashion Creator",
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    }

def get_youtube_trend_match(zip_code: str) -> List[Dict[str, Any]]:
    """
    Returns the top 10 YouTube creator videos for the selected ZIP code,
    with each matched to its most relevant catalog product (unique per video).
    If pinpulse_mock_db.json is present, reads from it. Otherwise, falls back.
    """
    logger.info(f"Retrieving top creator trends for zip_code: {zip_code}")

    # Load local catalog for catalog product mapping
    catalog = []
    if os.path.exists(LOCAL_CATALOG_FILE):
        try:
            with open(LOCAL_CATALOG_FILE, "r", encoding="utf-8") as f:
                catalog = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
    catalog_map = {p["id"]: p for p in catalog}

    # 1. Try loading from mock DB
    if os.path.exists(MOCK_DB_FILE):
        try:
            with open(MOCK_DB_FILE, "r", encoding="utf-8") as f:
                mock_records = json.load(f)
            
            # Filter creator records matching zip_code
            filtered = [r for r in mock_records if r.get("pincode") == zip_code and r.get("type") == "creator"]
            
            if filtered:
                # Group by video_id
                video_groups = {}
                for r in filtered:
                    vid = r.get("video_id")
                    if vid:
                        if vid not in video_groups:
                            video_groups[vid] = []
                        video_groups[vid].append(r)
                
                matched_results = []
                used_product_ids = set()

                for vid, records in list(video_groups.items())[:10]:
                    # Retrieve video details via oEmbed/Cache
                    v_meta = get_youtube_video_metadata(vid)
                    
                    # Gather tags and descriptions
                    all_tags = set()
                    descriptions = []
                    best_product = None

                    for r in records:
                        meta = r.get("metadata", {})
                        if "tags" in meta:
                            all_tags.update(meta["tags"])
                        desc = meta.get("description")
                        if desc:
                            descriptions.append(desc)
                        
                        # Find the first valid matched product
                        mp_id = r.get("matched_product_id")
                        if mp_id and not best_product and mp_id in catalog_map:
                            if mp_id not in used_product_ids:
                                best_product = catalog_map[mp_id]

                    # Fallback to any product if all are already matched
                    if not best_product and records:
                        for r in records:
                            mp_id = r.get("matched_product_id")
                            if mp_id and mp_id in catalog_map:
                                best_product = catalog_map[mp_id]
                                break

                    if best_product:
                        used_product_ids.add(best_product["id"])

                    # Construct merged description
                    llm_desc = " ".join(descriptions)[:200]
                    if len(descriptions) > 1:
                        llm_desc = f"Garments featured: " + ", ".join([r.get("metadata", {}).get("item", "apparel") for r in records])

                    youtube_video = {
                        "video_id": vid,
                        "title": v_meta["title"],
                        "channel": v_meta["channel"],
                        "thumbnail_url": v_meta["thumbnail_url"],
                        "video_url": f"https://www.youtube.com/watch?v={vid}",
                        "llm_extracted_description": llm_desc,
                        "inferred_tags": list(all_tags)
                    }

                    clean_product = None
                    if best_product:
                        clean_product = {k: v for k, v in best_product.items() if not k.endswith("_vector") and k != "embedding"}

                    matched_results.append({
                        "youtube_video": youtube_video,
                        "matched_product": clean_product
                    })

                logger.info(f"Successfully loaded {len(matched_results)} creator trends from pinpulse_mock_db.json.")
                return matched_results
        except Exception as e:
            logger.error(f"Error parsing mock DB for trends: {e}")

    # 2. Fallback to hardcoded mock feed (original behavior)
    logger.info("Falling back to hardcoded ZIP_CREATOR_VIDEOS.")
    videos = ZIP_CREATOR_VIDEOS.get(zip_code, ZIP_CREATOR_VIDEOS["800008"])

    matched_results = []
    used_product_ids = set()

    for video in videos:
        best_match = None
        best_score = -1
        target_tags = set(video["inferred_tags"])

        for product in catalog:
            product_id = product.get("id")
            if product_id in used_product_ids:
                continue

            product_tags = set(product.get("tags", []))
            desc_words = set(product.get("description", "").lower().split())

            overlap = len(target_tags.intersection(product_tags))
            desc_bonus = sum(1 for t in target_tags if t.split("-")[0] in desc_words) * 0.5
            score = overlap + desc_bonus

            if zip_code == "800008" and any(t in product_tags for t in ["saree", "silk", "traditional", "banarasi-silk", "tussar-saree"]):
                score += 3.0
            elif zip_code == "682001" and any(t in product_tags for t in ["kasavu_weave", "casual", "linen", "bohemian", "cotton"]):
                score += 3.0
            elif zip_code == "752001" and any(t in product_tags for t in ["sambalpuri", "traditional", "silk", "cotton", "ethnic"]):
                score += 3.0

            if score > best_score:
                best_score = score
                best_match = product

        matched_product_copy = None
        if best_match:
            used_product_ids.add(best_match.get("id"))
            matched_product_copy = {k: v for k, v in best_match.items() if not k.endswith("_vector") and k != "embedding"}
            overlap_list = list(target_tags.intersection(set(best_match.get("tags", []))))
            matched_product_copy["overlap_tags"] = overlap_list
            matched_product_copy["match_score"] = best_score

        matched_results.append({
            "youtube_video": video,
            "matched_product": matched_product_copy
        })

    return matched_results

