import os
import json
import logging
from typing import Dict, Any, List

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

logger = logging.getLogger("youtube_scraper")

# Curated list of 10 Creator Videos per ZIP code
ZIP_CREATOR_VIDEOS = {
    "560034": [  # Koramangala, Bengaluru - Streetwear & Gen-Z
        {
            "video_id": "vV_oO-UqC2c",
            "title": "Koramangala Thrift Store Haul & Streetwear Lookbook 👟",
            "channel": "Urban Vibe Feed",
            "thumbnail_url": "https://img.youtube.com/vi/vV_oO-UqC2c/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=vV_oO-UqC2c",
            "llm_extracted_description": "Oversized hoodies, baggy skater denims, and indie thrift finds styled for college campuses in Bengaluru.",
            "inferred_tags": ["streetwear", "hoodie", "baggy-jeans", "casual", "oversized-tees"]
        },
        {
            "video_id": "1F_U79tL_q8",
            "title": "Streetwear Shopping at Koramangala 5th Block | Budget Styling",
            "channel": "Drip Check India",
            "thumbnail_url": "https://img.youtube.com/vi/1F_U79tL_q8/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=1F_U79tL_q8",
            "llm_extracted_description": "Styling retro varsity jackets and cargo pants from local streetwear boutiques.",
            "inferred_tags": ["streetwear", "varsity-jackets", "cargo-pants", "casual"]
        },
        {
            "video_id": "dQw4w9WgXcQ", # Rickroll placeholder
            "title": "My Favorite Thrift Shops in Bengaluru! (Indie Thrift)",
            "channel": "Retro Closet",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Y2K crop tops and aesthetic streetwear apparel sourced from local thrift hubs.",
            "inferred_tags": ["y2k-crop", "streetwear", "casual", "modern"]
        },
        {
            "video_id": "vV_oO-UqC2c",
            "title": "Oversized Tees Try-On Haul | Streetwear Inspo",
            "channel": "Kora Drip",
            "thumbnail_url": "https://img.youtube.com/vi/vV_oO-UqC2c/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=vV_oO-UqC2c",
            "llm_extracted_description": "Oversized drop-shoulder tees styled with silver chains and retro shades.",
            "inferred_tags": ["oversized-tees", "streetwear", "casual"]
        },
        {
            "video_id": "1F_U79tL_q8",
            "title": "Huge Baggy Jeans Haul - Best Fits for College Students",
            "channel": "Vibe Check",
            "thumbnail_url": "https://img.youtube.com/vi/1F_U79tL_q8/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=1F_U79tL_q8",
            "llm_extracted_description": "Relaxed fit and extra baggy denims styled with sneakers.",
            "inferred_tags": ["baggy-jeans", "streetwear", "casual"]
        },
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Unboxing Varsity Jackets from Bengaluru Boutiques",
            "channel": "Hype Lab",
            "thought": "varsity jackets",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Reviewing premium streetwear varsity jackets with patch details.",
            "inferred_tags": ["varsity-jackets", "streetwear", "winter"]
        },
        {
            "video_id": "vV_oO-UqC2c",
            "title": "Retro Aesthetic Streetwear Styling Guide",
            "channel": "Indie retro",
            "thumbnail_url": "https://img.youtube.com/vi/vV_oO-UqC2c/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=vV_oO-UqC2c",
            "llm_extracted_description": "Y2K aesthetics, retro tees, and denim jackets styled for a casual weekend.",
            "inferred_tags": ["y2k-crop", "streetwear", "casual", "denim"]
        },
        {
            "video_id": "1F_U79tL_q8",
            "title": "Utility Cargo Pants Lookbook | Street Style",
            "channel": "Drip Lab",
            "thumbnail_url": "https://img.youtube.com/vi/1F_U79tL_q8/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=1F_U79tL_q8",
            "llm_extracted_description": "Multi-pocket utility cargoes styled with crop tops.",
            "inferred_tags": ["cargo-pants", "streetwear", "casual"]
        },
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Gen-Z Thrift Closet Tour | Bengaluru Streetwear Edition",
            "channel": "Vibe Studio",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Retro tees, oversized hoodies, and baggy jeans from local Bangalore micro-creators.",
            "inferred_tags": ["oversized-tees", "baggy-jeans", "streetwear"]
        },
        {
            "video_id": "vV_oO-UqC2c",
            "title": "Winter Layering in South India | Light Hoodies & Jackets",
            "channel": "Bangalore Style",
            "thumbnail_url": "https://img.youtube.com/vi/vV_oO-UqC2c/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=vV_oO-UqC2c",
            "llm_extracted_description": "Light hoodies and streetwear varsity jackets perfect for Bangalore weather.",
            "inferred_tags": ["hoodie", "varsity-jackets", "streetwear", "winter"]
        }
    ],
    "110049": [  # South Ext / Shahpur Jat, Delhi - Premium Fusion & Indo-Western
        {
            "video_id": "f_E_e3H6Rik",
            "title": "Shahpur Jat Bridal & Indo-Western Couture Boutique Tour 👗",
            "channel": "Delhi Luxury Edit",
            "thumbnail_url": "https://img.youtube.com/vi/f_E_e3H6Rik/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=f_E_e3H6Rik",
            "llm_extracted_description": "Premium pastel lehengas and designer draped Indo-western gowns showcasing heavy zari/chikankari embroidery details.",
            "inferred_tags": ["indo-western-gown", "pastel-lehenga", "chikankari-kurti", "traditional_embroidery", "ceremonial"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "Indo-Western Wedding Guest Gowns Haul | South Ext Shopping",
            "channel": "Couture Insider",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Draped Indo-western gowns and contemporary cocktail sarees for modern Delhi receptions.",
            "inferred_tags": ["indo-western-gown", "ceremonial", "ethnic", "festive"]
        },
        {
            "video_id": "y6120QOlsfU",
            "title": "Pastel Lehenga Trends for the 2026 Wedding Season",
            "channel": "Royal Threads",
            "thumbnail_url": "https://img.youtube.com/vi/y6120QOlsfU/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=y6120QOlsfU",
            "llm_extracted_description": "Beautiful mint and peach pastel lehengas with floral embroidery.",
            "inferred_tags": ["pastel-lehenga", "ethnic", "ceremonial", "festive"]
        },
        {
            "video_id": "f_E_e3H6Rik",
            "title": "Chikankari Kurti Styling Hacks | South Delhi Street Style",
            "channel": "Vastra Elegant",
            "thumbnail_url": "https://img.youtube.com/vi/f_E_e3H6Rik/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=f_E_e3H6Rik",
            "llm_extracted_description": "Styling georgette and cotton chikankari kurtis with oxidized jewelry.",
            "inferred_tags": ["chikankari-kurti", "ethnic", "casual", "summer"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "How to Style a Designer Dupatta 5 Ways | Fusion Lookbook",
            "channel": "Design Exclusives",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Heavy embroidered designer dupattas paired with simple solid anarkalis.",
            "inferred_tags": ["designer-dupatta", "ethnic", "traditional", "festive"]
        },
        {
            "video_id": "y6120QOlsfU",
            "title": "Premium Indo-Western Gown Showcase - Monika & Nidhi Label",
            "channel": "Delhi Couture",
            "thumbnail_url": "https://img.youtube.com/vi/y6120QOlsfU/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=y6120QOlsfU",
            "llm_extracted_description": "Reviewing sequined Indo-western drape gowns with cape sleeves.",
            "inferred_tags": ["indo-western-gown", "ethnic", "festive", "party"]
        },
        {
            "video_id": "f_E_e3H6Rik",
            "title": "Pastel Bridal Outfits Haul from Frontier Raas Delhi",
            "channel": "Royal Boutique",
            "thumbnail_url": "https://img.youtube.com/vi/f_E_e3H6Rik/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=f_E_e3H6Rik",
            "llm_extracted_description": "Unboxing pastel mint green lehengas and gold border dupattas.",
            "inferred_tags": ["pastel-lehenga", "designer-dupatta", "ceremonial", "festive"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "Luxury Chikankari Kurtis Collection Tour - South Ext",
            "channel": "Zari Label",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Reviewing handwoven pastel chikankari kurtis with delicate mirror work.",
            "inferred_tags": ["chikankari-kurti", "ethnic", "traditional", "festive"]
        },
        {
            "video_id": "y6120QOlsfU",
            "title": "Delhi Cocktail Party Gown Trends | Modern Fusion wear",
            "channel": "Elegant Gallery",
            "thumbnail_url": "https://img.youtube.com/vi/y6120QOlsfU/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=y6120QOlsfU",
            "llm_extracted_description": "Emerald green draped reception gowns and Indo-western fusion wear.",
            "inferred_tags": ["indo-western-gown", "ethnic", "party", "formal"]
        },
        {
            "video_id": "f_E_e3H6Rik",
            "title": "Traditional Banarasi Shawls & Silk Dupattas Collection",
            "channel": "Vastra House",
            "thumbnail_url": "https://img.youtube.com/vi/f_E_e3H6Rik/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=f_E_e3H6Rik",
            "llm_extracted_description": "Heavy embroidered designer silk dupattas and wool-mix Banarasi shawls.",
            "inferred_tags": ["designer-dupatta", "ethnic", "traditional", "winter"]
        }
    ],
    "800001": [  # Frazer Road, Patna - Traditional Silk & Wedding
        {
            "video_id": "E5616gG4bCw",
            "title": "Patna Ethnic Tussar & Banarasi Silk Saree Collection Haul 🥻",
            "channel": "Bihari Heritage Couture",
            "thumbnail_url": "https://img.youtube.com/vi/E5616gG4bCw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=E5616gG4bCw",
            "llm_extracted_description": "Traditional pure silk Banarasi and tussar handloom sarees in festive colors with intricate borders, curated for weddings.",
            "inferred_tags": ["banarasi-silk", "tussar-saree", "heavy-anarkali", "traditional", "silk", "saree"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "Best Banarasi Silk Saree Shops in Patna | Dulhan Wear",
            "channel": "Patna Weddings",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Reviewing thick gold zari border Banarasi silk sarees in royal red and crimson.",
            "inferred_tags": ["banarasi-silk", "saree", "silk", "traditional", "ceremonial"]
        },
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Tussar Silk Sarees Lookbook | Bhagalpur Handloom Saree Tour",
            "channel": "Mayur Emporium",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Authentic local tussar silk sarees showing off natural golden sheen and traditional printing.",
            "inferred_tags": ["tussar-saree", "saree", "silk", "traditional", "ethnic"]
        },
        {
            "video_id": "E5616gG4bCw",
            "title": "Heavy Anarkali Suits Try-On Haul | Wedding Guest Inspo",
            "channel": "Shree Ethnic Wear",
            "thumbnail_url": "https://img.youtube.com/vi/E5616gG4bCw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=E5616gG4bCw",
            "llm_extracted_description": "Floor-length heavy embroidered anarkali sets with designer organza dupattas.",
            "inferred_tags": ["heavy-anarkali", "ethnic", "festive", "traditional"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "Festive Kurta Sets for Groom & Guests | Patna Vivah Boutique",
            "channel": "Bandhan Saree Niketan",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Bright colored cotton and silk festive kurta sets styled with Nehru jackets.",
            "inferred_tags": ["festive-kurta-set", "ethnic", "traditional", "festive"]
        },
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Dulhan Red Banarasi Silk Saree Special - Patna Vastra Bhandar",
            "channel": "Dulhan Saree",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Pure katan silk bridal Banarasi saree with heavy golden brocade.",
            "inferred_tags": ["banarasi-silk", "saree", "silk", "ceremonial", "traditional"]
        },
        {
            "video_id": "E5616gG4bCw",
            "title": "Raw Tussar Silk Saree Handloom Unboxing",
            "channel": "Patna Ethnic Wear",
            "thumbnail_url": "https://img.youtube.com/vi/E5616gG4bCw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=E5616gG4bCw",
            "llm_extracted_description": "Bhagalpuri tussar silk sarees with modern block prints and traditional borders.",
            "inferred_tags": ["tussar-saree", "saree", "silk", "ethnic", "traditional"]
        },
        {
            "video_id": "jNQXAC9IVRw",
            "title": "Heavy Designer Anarkali Gowns Collection",
            "channel": "Rani Boutique",
            "thumbnail_url": "https://img.youtube.com/vi/jNQXAC9IVRw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "llm_extracted_description": "Floor-touch georgette and velvet heavy anarkali kurtis with stone embroidery.",
            "inferred_tags": ["heavy-anarkali", "ethnic", "festive", "traditional"]
        },
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "Chhath Puja Festive Wear Kurtas & Silk Dupattas Tour",
            "channel": "Vastra Bhandar",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "llm_extracted_description": "Turmeric yellow cotton kurtas and heavy tussar silk dupattas perfect for festivals.",
            "inferred_tags": ["festive-kurta-set", "tussar-saree", "ethnic", "festive"]
        },
        {
            "video_id": "E5616gG4bCw",
            "title": "Engagement Heavy Anarkali & Bridal Saree Unboxing",
            "channel": "Vivah Emporium",
            "thumbnail_url": "https://img.youtube.com/vi/E5616gG4bCw/maxresdefault.jpg",
            "video_url": "https://www.youtube.com/watch?v=E5616gG4bCw",
            "llm_extracted_description": "Royal Banarasi sarees and matching heavy ethnic suits for wedding functions.",
            "inferred_tags": ["banarasi-silk", "heavy-anarkali", "saree", "traditional"]
        }
    ]
}

def get_youtube_trend_match(zip_code: str) -> List[Dict[str, Any]]:
    """
    Returns the top 10 YouTube creator videos for the selected ZIP code,
    with each matched to its most relevant catalog product.
    """
    logger.info(f"Retrieving top 10 creator trends for zip_code: {zip_code}")
    
    # Handle zip mappings for backward compatibility
    zip_mapping = {
        "800008": "800001", # Patna
        "682001": "560034", # Kochi -> Bengaluru Koramangala
        "752001": "110049"  # Odisha -> Delhi South Ext
    }
    target_zip = zip_mapping.get(zip_code, zip_code)
    
    videos = ZIP_CREATOR_VIDEOS.get(target_zip, ZIP_CREATOR_VIDEOS["560034"])
    
    if not os.path.exists(LOCAL_CATALOG_FILE):
        return []
        
    try:
        with open(LOCAL_CATALOG_FILE, "r") as f:
            catalog = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load catalog: {e}")
        return []
        
    matched_results = []
    
    for video in videos:
        best_match = None
        best_score = -1
        target_tags = set(video["inferred_tags"])
        
        for product in catalog:
            product_tags = set(product.get("tags", []))
            
            # Calculate tag overlap
            overlap = len(target_tags.intersection(product_tags))
            score = overlap * 1.0
            
            # Add strict regional surges
            if target_zip == "800001" and "banarasi-silk" in product_tags:
                score += 5.0
            elif target_zip == "560034" and "streetwear" in product_tags:
                score += 5.0
            elif target_zip == "110049" and "indo-western-gown" in product_tags:
                score += 5.0
                
            # Geographic filter
            p_zips = product.get("zip_codes", [])
            if p_zips and target_zip not in p_zips and zip_code not in p_zips:
                continue
                
            if score > best_score:
                best_score = score
                best_match = product
                
        # Clone matched product to avoid mutating catalog cache
        matched_product_copy = None
        if best_match:
            matched_product_copy = dict(best_match)
            overlap_list = list(target_tags.intersection(set(best_match.get("tags", []))))
            matched_product_copy["overlap_tags"] = overlap_list
            matched_product_copy["match_score"] = best_score
            
        matched_results.append({
            "youtube_video": video,
            "matched_product": matched_product_copy
        })
        
    return matched_results
