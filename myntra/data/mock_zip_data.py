"""
Mock ZIP Code Data, Weather Rules, Festival Rules, Creators, and Stores.
"""

import numpy as np


def generate_vector(seed_text, dim=64):
    """Generate a deterministic pseudo-vector from a seed string."""
    np.random.seed(hash(seed_text) % (2**32))
    vec = np.random.randn(dim)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()


# =============================================================================
# ZIP CODE TABLE
# =============================================================================

ZIP_DATA = {
    "800008": {
        "city": "Patna",
        "state": "Bihar",
        "weather_conditions": "hot_humid",
        "active_festival": "chhath_puja",
        "aov": 1800,
    },
    "530001": {
        "city": "Vizag",
        "state": "Andhra Pradesh",
        "weather_conditions": "hot_humid",
        "active_festival": None,
        "aov": 2200,
    },
    "641001": {
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "weather_conditions": "warm_moderate",
        "active_festival": "pongal",
        "aov": 2000,
    },
    "590001": {
        "city": "Belgaum",
        "state": "Karnataka",
        "weather_conditions": "warm_moderate",
        "active_festival": None,
        "aov": 1500,
    },
    "110001": {
        "city": "Delhi",
        "state": "Delhi",
        "weather_conditions": "hot_dry",
        "active_festival": "diwali",
        "aov": 3500,
    },
}

# =============================================================================
# WEATHER RULES TABLE
# =============================================================================

WEATHER_RULES = {
    "hot_humid": {
        "allowable_materials": ["cotton", "linen", "rayon", "chiffon", "georgette"],
        "description": "Breathable cotton and linen, absorbs sweat, ideal for hot and humid tropical climates",
        "vector": generate_vector("breathable cotton linen absorbs sweat hot humid tropical climate"),
    },
    "warm_moderate": {
        "allowable_materials": ["cotton", "rayon", "crepe", "silk", "chanderi"],
        "description": "Light cotton and rayon blends, comfortable for warm moderate climates",
        "vector": generate_vector("light cotton rayon comfortable warm moderate climate"),
    },
    "hot_dry": {
        "allowable_materials": ["cotton", "linen", "khadi", "chanderi"],
        "description": "Loose cotton and linen, protects from dry heat, allows air circulation",
        "vector": generate_vector("loose cotton linen dry heat air circulation breathable"),
    },
    "cold": {
        "allowable_materials": ["velvet", "wool", "silk", "brocade"],
        "description": "Warm velvet and wool, insulating fabrics for cold winter weather",
        "vector": generate_vector("warm velvet wool insulating cold winter weather layers"),
    },
}

# =============================================================================
# FESTIVAL RULES TABLE
# =============================================================================

FESTIVAL_RULES = {
    "chhath_puja": {
        "festival_name": "Chhath Puja",
        "target_color": "yellow",
        "target_nature": "ethnic",
        "description": "Traditional ethnic Chhath Puja celebration, yellow and red colors dominate",
        "vector": generate_vector("traditional ethnic yellow red chhath puja festive cultural Bihar celebration"),
    },
    "diwali": {
        "festival_name": "Diwali",
        "target_color": "gold",
        "target_nature": "festive",
        "description": "Grand festive Diwali celebration, gold and red heavily embellished outfits",
        "vector": generate_vector("grand festive Diwali gold red embellished lights celebration ethnic"),
    },
    "pongal": {
        "festival_name": "Pongal",
        "target_color": "yellow",
        "target_nature": "ethnic",
        "description": "Traditional Pongal harvest festival, yellow silk sarees and ethnic wear",
        "vector": generate_vector("traditional Pongal harvest yellow silk saree Tamil ethnic celebration"),
    },
    "eid": {
        "festival_name": "Eid",
        "target_color": "green",
        "target_nature": "festive",
        "description": "Elegant Eid celebration, green and white festive occasion wear",
        "vector": generate_vector("elegant Eid green white festive celebration occasion ethnic"),
    },
}

# =============================================================================
# CREATORS DATA (per ZIP code — 5 creators each)
# =============================================================================

CREATORS = {
    "800008": [
        {
            "name": "Patna Style Diaries",
            "youtube_url": "https://youtube.com/patna_style",
            "demographic": "gen-z",
            "subscriber_weight": 1.5,
            "vector": generate_vector("Gen-Z festive ethnic yellow saree traditional Bihar Patna trendy"),
            "confidence_score": 0.9,
        },
        {
            "name": "Bihar Fashion Hub",
            "youtube_url": "https://youtube.com/bihar_fashion",
            "demographic": "millennial",
            "subscriber_weight": 1.2,
            "vector": generate_vector("Millennial ethnic silk maroon gold traditional festive wedding Bihar"),
            "confidence_score": 0.85,
        },
        {
            "name": "Desi Glam Patna",
            "youtube_url": "https://youtube.com/desi_glam",
            "demographic": "gen-z",
            "subscriber_weight": 1.0,
            "vector": generate_vector("Gen-Z fusion streetwear ethnic modern Indo-western colorful Patna"),
            "confidence_score": 0.8,
        },
        {
            "name": "Traditional Vibes",
            "youtube_url": "https://youtube.com/trad_vibes",
            "demographic": "millennial",
            "subscriber_weight": 1.3,
            "vector": generate_vector("Millennial traditional saree cotton handloom ethnic daily wear"),
            "confidence_score": 0.92,
        },
        {
            "name": "Patna Trending Now",
            "youtube_url": "https://youtube.com/patna_trending",
            "demographic": "gen-z",
            "subscriber_weight": 1.0,
            "vector": generate_vector("Gen-Z trendy casual ethnic kurta jeans fusion affordable Patna"),
            "confidence_score": 0.75,
        },
    ],
    "530001": [
        {
            "name": "Vizag Vogue",
            "youtube_url": "https://youtube.com/vizag_vogue",
            "demographic": "gen-z",
            "subscriber_weight": 1.4,
            "vector": generate_vector("Gen-Z breezy cotton coastal Vizag summer colors trendy casual"),
            "confidence_score": 0.88,
        },
        {
            "name": "AP Style Queen",
            "youtube_url": "https://youtube.com/ap_style",
            "demographic": "millennial",
            "subscriber_weight": 1.1,
            "vector": generate_vector("Millennial South Indian silk saree traditional Andhra elegant ethnic"),
            "confidence_score": 0.9,
        },
        {
            "name": "Beach City Fashion",
            "youtube_url": "https://youtube.com/beach_fashion",
            "demographic": "gen-z",
            "subscriber_weight": 1.0,
            "vector": generate_vector("Gen-Z beachwear casual cotton dresses summer Vizag coastal vibes"),
            "confidence_score": 0.82,
        },
        {
            "name": "South Ethnic Diaries",
            "youtube_url": "https://youtube.com/south_ethnic",
            "demographic": "millennial",
            "subscriber_weight": 1.2,
            "vector": generate_vector("Millennial Kanjeevaram silk traditional South Indian wedding bridal"),
            "confidence_score": 0.87,
        },
        {
            "name": "Vizag Street Style",
            "youtube_url": "https://youtube.com/vizag_street",
            "demographic": "gen-z",
            "subscriber_weight": 1.0,
            "vector": generate_vector("Gen-Z streetwear casual denim t-shirt sneakers urban Vizag youth"),
            "confidence_score": 0.78,
        },
    ],
    "641001": [
        {
            "name": "Kovai Fashionista",
            "youtube_url": "https://youtube.com/kovai_fashion",
            "demographic": "millennial",
            "subscriber_weight": 1.5,
            "vector": generate_vector("Millennial silk saree Coimbatore traditional Pongal yellow ethnic"),
            "confidence_score": 0.91,
        },
        {
            "name": "Tamil Style Studio",
            "youtube_url": "https://youtube.com/tamil_style",
            "demographic": "gen-z",
            "subscriber_weight": 1.3,
            "vector": generate_vector("Gen-Z modern ethnic cotton kurta Coimbatore trendy fusion South"),
            "confidence_score": 0.86,
        },
        {
            "name": "Coimbatore Trends",
            "youtube_url": "https://youtube.com/cbe_trends",
            "demographic": "millennial",
            "subscriber_weight": 1.0,
            "vector": generate_vector("Millennial traditional cotton saree handloom Coimbatore classic daily"),
            "confidence_score": 0.84,
        },
        {
            "name": "South Gen-Z Style",
            "youtube_url": "https://youtube.com/south_genz",
            "demographic": "gen-z",
            "subscriber_weight": 1.1,
            "vector": generate_vector("Gen-Z casual western crop top jeans sneakers Coimbatore youth"),
            "confidence_score": 0.79,
        },
        {
            "name": "Ethnic Express TN",
            "youtube_url": "https://youtube.com/ethnic_tn",
            "demographic": "millennial",
            "subscriber_weight": 1.2,
            "vector": generate_vector("Millennial silk organza festive occasion wear Tamil Nadu elegant"),
            "confidence_score": 0.88,
        },
    ],
}

# =============================================================================
# LOCAL STORES / BOUTIQUES DATA (per ZIP code)
# =============================================================================

STORES = {
    "800008": [
        {
            "name": "Kalyan Silks Patna",
            "rating": 4.6,
            "review_count": 1200,
            "estimated_cost": 2500,
            "vector": generate_vector("traditional silk saree festive ethnic heavy embroidered Patna bridal"),
        },
        {
            "name": "Manyavar Patna",
            "rating": 4.3,
            "review_count": 800,
            "estimated_cost": 3000,
            "vector": generate_vector("festive ethnic kurta set velvet silk wedding occasion Patna"),
        },
        {
            "name": "Patna Fashion House",
            "rating": 4.1,
            "review_count": 350,
            "estimated_cost": 1500,
            "vector": generate_vector("affordable ethnic casual cotton kurti daily wear Patna budget"),
        },
    ],
    "530001": [
        {
            "name": "Vizag Silk House",
            "rating": 4.5,
            "review_count": 600,
            "estimated_cost": 2800,
            "vector": generate_vector("South Indian silk saree traditional Vizag elegant Kanjeevaram"),
        },
        {
            "name": "Modern Trends Vizag",
            "rating": 4.0,
            "review_count": 200,
            "estimated_cost": 1800,
            "vector": generate_vector("modern fusion ethnic casual daily wear affordable Vizag trendy"),
        },
        {
            "name": "Coastal Chic Boutique",
            "rating": 4.7,
            "review_count": 90,
            "estimated_cost": 2200,
            "vector": generate_vector("breezy coastal cotton rayon casual western beach Vizag summer"),
        },
    ],
    "641001": [
        {
            "name": "Coimbatore Silks",
            "rating": 4.8,
            "review_count": 2500,
            "estimated_cost": 3500,
            "vector": generate_vector("premium Kanjeevaram silk saree Coimbatore traditional wedding bridal"),
        },
        {
            "name": "Kovai Cotton House",
            "rating": 4.4,
            "review_count": 450,
            "estimated_cost": 1200,
            "vector": generate_vector("handloom cotton saree Coimbatore daily ethnic affordable traditional"),
        },
        {
            "name": "TN Ethnic Emporium",
            "rating": 4.2,
            "review_count": 300,
            "estimated_cost": 2000,
            "vector": generate_vector("Tamil Nadu ethnic festive occasion silk organza elegant Coimbatore"),
        },
    ],
}

# =============================================================================
# CO-PURCHASE (COLLABORATIVE FILTERING) LOOKUP
# =============================================================================

CF_LOOKUP = {
    "prod_001": {
        "cluster_id": "festive_ethnic_maroon",
        "recommendations": [
            {"id": "prod_012", "strength": 0.90},
            {"id": "prod_045", "strength": 0.65},
            {"id": "prod_102", "strength": 0.25},
        ],
    },
    "prod_003": {
        "cluster_id": "festive_lehenga_blue",
        "recommendations": [
            {"id": "prod_025", "strength": 0.85},
            {"id": "prod_078", "strength": 0.60},
            {"id": "prod_110", "strength": 0.40},
        ],
    },
    "prod_007": {
        "cluster_id": "festive_anarkali_yellow",
        "recommendations": [
            {"id": "prod_056", "strength": 0.80},
            {"id": "prod_025", "strength": 0.55},
            {"id": "prod_012", "strength": 0.30},
        ],
    },
    "prod_012": {
        "cluster_id": "festive_ethnic_maroon",
        "recommendations": [
            {"id": "prod_001", "strength": 0.85},
            {"id": "prod_045", "strength": 0.50},
            {"id": "prod_088", "strength": 0.35},
        ],
    },
    "prod_025": {
        "cluster_id": "festive_accessories_gold",
        "recommendations": [
            {"id": "prod_060", "strength": 0.75},
            {"id": "prod_078", "strength": 0.60},
            {"id": "prod_098", "strength": 0.30},
        ],
    },
    "prod_045": {
        "cluster_id": "festive_ethnic_maroon",
        "recommendations": [
            {"id": "prod_001", "strength": 0.70},
            {"id": "prod_012", "strength": 0.65},
            {"id": "prod_088", "strength": 0.45},
        ],
    },
    "prod_056": {
        "cluster_id": "ethnic_cotton_yellow",
        "recommendations": [
            {"id": "prod_007", "strength": 0.75},
            {"id": "prod_091", "strength": 0.55},
            {"id": "prod_005", "strength": 0.40},
        ],
    },
    "prod_088": {
        "cluster_id": "festive_ethnic_red",
        "recommendations": [
            {"id": "prod_012", "strength": 0.80},
            {"id": "prod_001", "strength": 0.60},
            {"id": "prod_045", "strength": 0.45},
        ],
    },
    "prod_091": {
        "cluster_id": "casual_ethnic_cotton",
        "recommendations": [
            {"id": "prod_005", "strength": 0.70},
            {"id": "prod_022", "strength": 0.55},
            {"id": "prod_056", "strength": 0.35},
        ],
    },
    "prod_010": {
        "cluster_id": "evergreen_basics",
        "recommendations": [
            {"id": "prod_018", "strength": 0.80},
            {"id": "prod_030", "strength": 0.70},
            {"id": "prod_072", "strength": 0.50},
        ],
    },
}
