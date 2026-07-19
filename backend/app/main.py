import os
import json
import logging
import numpy as np
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pinpulse_api")

load_dotenv()

app = FastAPI(title="PinPulse - Myntra Hyper-Local Tri-Layer Engine API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

# Import recommender engine components
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config import CONTEXT_MATRICES, INTENT_DECAY_CONFIG
from scoring_engine import (
    cosine_similarity,
    normalize_cosine_score,
    calculate_aesthetic_score,
    calculate_fabric_score,
    calculate_festivity_score,
    calculate_creator_score,
    calculate_boutique_score,
    calculate_velocity_score,
)
from pinpulse_engine import PinPulseEngine

# Mappings & Caches
ZIP_MAPPING = {
    "800001": "800008", # Frazer Road -> Patna
    "560034": "682001", # Koramangala -> Kochi
    "752001": "752001", # Puri -> Odisha
}

# Fallback calendar data when offline
FALLBACK_CALENDAR = {
    # Patna
    ("800008", "2026-11-15"): {"event_name": "Chhath Puja (Sandhya Arghya)", "event_type": "festival", "attire_tags": ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath_puja"], "is_festive": True},
    ("800008", "2026-02-02"): {"event_name": "Saraswati Puja (Vasant Panchami)", "event_type": "festival", "attire_tags": ["saree", "kurta", "yellow", "ethnic"], "is_festive": True},
    ("800008", "2026-03-22"): {"event_name": "Bihar Diwas (Bihar Day)", "event_type": "festival", "attire_tags": ["saree", "salwar", "bhagalpuri_silk", "kurta", "dhoti", "nehru_jacket", "white", "cream", "patna"], "is_festive": True},
    ("800008", "2026-12-10"): {"event_name": "Patna Wedding Day (Pheras)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "traditional_embroidery", "ceremonial", "silk", "saree", "sherwani", "crimson", "gold", "maroon"], "is_festive": True},
    # Kochi
    ("682001", "2026-01-20"): {"event_name": "Kochi-Muziris Biennale Peak", "event_type": "festival", "attire_tags": ["artsy", "bohemian", "linen", "sustainable", "modern"], "is_festive": True},
    ("682001", "2026-04-14"): {"event_name": "Vishu Festival (Malayali New Year)", "event_type": "festival", "attire_tags": ["ethnic", "yellow", "gold", "cream", "kasavu_weave"], "is_festive": True},
    ("682001", "2026-08-27"): {"event_name": "Onam Festival (Thiruvonam)", "event_type": "festival", "attire_tags": ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"], "is_festive": True},
    ("682001", "2026-12-27"): {"event_name": "Kochi Wedding Day (Thalikettu)", "event_type": "wedding_day", "attire_tags": ["kasavu_weave", "off-white", "cream", "gold"], "is_festive": True},
    # Odisha
    ("752001", "2026-01-14"): {"event_name": "Makar Sankranti (Makar Mela)", "event_type": "festival", "attire_tags": ["traditional", "tussar_silk", "yellow", "red", "odisha"], "is_festive": True},
    ("752001", "2026-06-14"): {"event_name": "Pahili Raja (Raja Parba)", "event_type": "festival", "attire_tags": ["traditional", "cotton", "pastel", "lightweight", "sambalpuri"], "is_festive": True},
    ("752001", "2026-06-15"): {"event_name": "Raja Sankranti Festival", "event_type": "festival", "attire_tags": ["traditional", "cotton", "pastel", "sambalpuri", "ethnic"], "is_festive": True},
    ("752001", "2026-07-16"): {"event_name": "Puri Rath Yatra Chariot Festival", "event_type": "festival", "attire_tags": ["sambalpuri", "cotton", "traditional", "yellow", "saffron", "saree", "kurta"], "is_festive": True},
    ("752001", "2026-12-20"): {"event_name": "Odisha Winter Wedding (Pheras)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "tussar_silk", "ceremonial", "sherwani", "crimson", "gold"], "is_festive": True},
}

# Weather Matrix throughout the year
WEATHER_MATRIX = {
    "800008": { # Patna
        1: {"desc": "Cold & Foggy ❄️", "temp": "10°C–22°C", "cold_wave": True, "hot_wave": False, "rainy": False, "weather_conditions": "cold"},
        2: {"desc": "Cool & Sunny 🌤️", "temp": "12°C–26°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "cold"},
        3: {"desc": "Warming Up ☀️", "temp": "17°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        4: {"desc": "Hot & Dry 🔥", "temp": "21°C–38°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_dry"},
        5: {"desc": "Very Hot 🔥", "temp": "24°C–39°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_dry"},
        6: {"desc": "Hot & Humid 🌡️", "temp": "25°C–35°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        7: {"desc": "Hot & Monsoon 🌧️", "temp": "26°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        8: {"desc": "Humid & Wet 🌧️", "temp": "25°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        9: {"desc": "Humid 🌧️", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        10: {"desc": "Pleasant 🍂", "temp": "20°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        11: {"desc": "Cool & Dry 🍂", "temp": "15°C–27°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        12: {"desc": "Cold & Dry ❄️", "temp": "11°C–23°C", "cold_wave": True, "hot_wave": False, "rainy": False, "weather_conditions": "cold"}
    },
    "682001": { # Fort Kochi
        1: {"desc": "Pleasant & Dry 🍃", "temp": "23°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        2: {"desc": "Pleasant & Dry 🍃", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        3: {"desc": "Warm & Humid 🌡️", "temp": "25°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "hot_humid"},
        4: {"desc": "Hot & Humid 🔥", "temp": "27°C–33°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        5: {"desc": "Hot & Wet 🌧️", "temp": "27°C–31°C", "cold_wave": False, "hot_wave": True, "rainy": True, "weather_conditions": "hot_humid"},
        6: {"desc": "Wet/Monsoon 🌧️", "temp": "26°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        7: {"desc": "Peak Monsoon 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        8: {"desc": "Monsoon 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        9: {"desc": "Monsoon Subsiding 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        10: {"desc": "Warm & Humid 🌡️", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "hot_humid"},
        11: {"desc": "Warm & Dry ☀️", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        12: {"desc": "Pleasant & Dry 🍃", "temp": "24°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"}
    },
    "752001": { # Puri, Odisha
        1: {"desc": "Cool & Pleasant 🍃", "temp": "18°C–27°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        2: {"desc": "Pleasant & Sunny ☀️", "temp": "21°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        3: {"desc": "Warm & Sunny ☀️", "temp": "24°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "hot_humid"},
        4: {"desc": "Hot & Humid 🔥", "temp": "27°C–35°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        5: {"desc": "Very Hot & Humid 🔥", "temp": "28°C–37°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        6: {"desc": "Monsoon Showers 🌧️", "temp": "27°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        7: {"desc": "Heavy Monsoons 🌧️", "temp": "26°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        8: {"desc": "Wet & Humid 🌧️", "temp": "26°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        9: {"desc": "Breezy Showers 🌧️", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        10: {"desc": "Pleasant Autumn 🍂", "temp": "23°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        11: {"desc": "Cool & Dry 🍂", "temp": "20°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        12: {"desc": "Mild Winter ❄️", "temp": "17°C–26°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"}
    }
}

# Try loading weather matrix from dynamic JSON seeder cache
weather_cache_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "weather_presets.json"))
if os.path.exists(weather_cache_file):
    try:
        with open(weather_cache_file, "r", encoding="utf-8") as f:
            raw_weather = json.load(f)
            # Convert month keys from strings to integers
            converted_weather = {}
            for z, months in raw_weather.items():
                converted_weather[z] = {int(m): data for m, data in months.items()}
            WEATHER_MATRIX = converted_weather
            logger.info("Successfully loaded weather insights cache.")
    except Exception as e:
        logger.error(f"Failed to load weather insights cache: {e}")

# Weather Rules vectors
def generate_vector(seed_text):
    np.random.seed(hash(seed_text) % (2**32))
    vec = np.random.randn(512)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

WEATHER_RULES = {
    "hot_humid": {
        "allowable_materials": ["cotton", "linen", "rayon", "chiffon", "georgette"],
        "vector": generate_vector("breathable cotton linen absorbs sweat hot humid tropical climate"),
    },
    "warm_moderate": {
        "allowable_materials": ["cotton", "rayon", "crepe", "silk", "chanderi"],
        "vector": generate_vector("light cotton rayon comfortable warm moderate climate"),
    },
    "hot_dry": {
        "allowable_materials": ["cotton", "linen", "khadi", "chanderi"],
        "vector": generate_vector("loose cotton linen dry heat air circulation breathable"),
    },
    "cold": {
        "allowable_materials": ["velvet", "wool", "silk", "brocade"],
        "vector": generate_vector("warm velvet wool insulating cold winter weather layers"),
    },
}

# Festival Rules vectors
FESTIVAL_RULES = {
    "chhath_puja": {
        "target_color": "yellow",
        "target_nature": "ethnic",
        "vector": generate_vector("traditional ethnic yellow red chhath puja festive cultural Bihar celebration"),
    },
    "diwali": {
        "target_color": "gold",
        "target_nature": "festive",
        "vector": generate_vector("glowing gold silk brocade traditional diwali festive lights deepavali"),
    },
    "pongal": {
        "target_color": "white",
        "target_nature": "traditional",
        "vector": generate_vector("pongal harvest traditional white gold border south indian cotton"),
    },
    "eid": {
        "target_color": "green",
        "target_nature": "festive",
        "vector": generate_vector("festive ethnic embroidered traditional green gold eid celebration modest"),
    },
}

# Co-Purchase Collaborative Filtering pairings (using integer IDs)
CF_LOOKUP = {
    1: {
        "cluster_id": "festive_ethnic_crimson",
        "recommendations": [
            {"id": 124, "strength": 0.90},
            {"id": 149, "strength": 0.65},
            {"id": 15, "strength": 0.25},
        ]
    },
    2: {
        "cluster_id": "festive_ethnic_maroon",
        "recommendations": [
            {"id": 124, "strength": 0.85},
            {"id": 149, "strength": 0.60},
        ]
    },
    9: {
        "cluster_id": "festive_ethnic_yellow",
        "recommendations": [
            {"id": 127, "strength": 0.85},
            {"id": 149, "strength": 0.60},
        ]
    },
    7: {
        "cluster_id": "festive_chhath_yellow",
        "recommendations": [
            {"id": 127, "strength": 0.80},
        ]
    },
    16: {
        "cluster_id": "festive_onam_white",
        "recommendations": [
            {"id": 127, "strength": 0.80},
        ]
    },
    97: {
        "cluster_id": "festive_kochi_wedding",
        "recommendations": [
            {"id": 124, "strength": 0.85},
            {"id": 149, "strength": 0.60},
        ]
    },
    110: {
        "cluster_id": "streetwear_shillong_cherry",
        "recommendations": [
            {"id": 38, "strength": 0.85},
            {"id": 149, "strength": 0.70},
        ]
    },
    112: {
        "cluster_id": "festive_winter_velvet",
        "recommendations": [
            {"id": 135, "strength": 0.85},
            {"id": 149, "strength": 0.70},
        ]
    }
}

# Fallback Creators database representation
FALLBACK_CREATORS = {
    "800008": [
        {
            "id": 1,
            "name": "Patna Ethnic Wear Vlog",
            "youtube_url": "https://youtube.com/patna_ethnic",
            "demographic": "millennial",
            "subscriber_count": 150000,
            "subscriber_weight": 1.2,
            "vector": generate_vector("Millennial traditional saree cotton handloom ethnic daily wear"),
            "videos": [
                {
                    "id": 101,
                    "video_url": "https://youtube.com/watch?v=patna_wed_1",
                    "title": "Top Patna Wedding Lehengas & Sherwanis 2026",
                    "description": "Traditional pure silk Banarasi and tussar handloom sarees in festive colors.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8",
                    "simulated_engagement": 18000,
                    "product_ids": [1, 2]
                },
                {
                    "id": 102,
                    "video_url": "https://youtube.com/watch?v=patna_mkt_2",
                    "title": "Affordable Kurtis at Patna Market Tour",
                    "description": "Exploring local street shops for festive cotton and silk kurtis.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c",
                    "simulated_engagement": 8500,
                    "product_ids": [7, 9]
                }
            ]
        },
        {
            "id": 2,
            "name": "Traditional Vibes",
            "youtube_url": "https://youtube.com/trad_vibes",
            "demographic": "millennial",
            "subscriber_count": 98000,
            "subscriber_weight": 1.3,
            "vector": generate_vector("Millennial traditional saree cotton handloom ethnic daily wear"),
            "videos": [
                {
                    "id": 103,
                    "video_url": "https://youtube.com/watch?v=trad_vibes_1",
                    "title": "Saraswati Puja Yellow Saree Styling Guide",
                    "description": "Styling bright yellow georgette sarees with traditional matching anklets and light makeup.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c",
                    "simulated_engagement": 12000,
                    "product_ids": [9]
                }
            ]
        },
        {
            "id": 3,
            "name": "Patna Trending Now",
            "youtube_url": "https://youtube.com/patna_trending",
            "demographic": "gen-z",
            "subscriber_count": 75000,
            "subscriber_weight": 1.0,
            "vector": generate_vector("Gen-Z trendy casual ethnic kurta jeans fusion affordable Patna"),
            "videos": [
                {
                    "id": 104,
                    "video_url": "https://youtube.com/watch?v=patna_trend_1",
                    "title": "Gen-Z Fusion Kurta Styling Tips",
                    "description": "Styling short kurtis with relaxed fit denim and sneakers for everyday comfort.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
                    "simulated_engagement": 7500,
                    "product_ids": [9]
                }
            ]
        }
    ],
    "682001": [
        {
            "id": 4,
            "name": "Kochi Couture",
            "youtube_url": "https://youtube.com/kochi_couture",
            "demographic": "millennial",
            "subscriber_count": 320000,
            "subscriber_weight": 1.3,
            "vector": generate_vector("Millennial traditional South Indian silk saree white gold cream Mundu"),
            "videos": [
                {
                    "id": 105,
                    "video_url": "https://youtube.com/watch?v=kochi_kasavu_1",
                    "title": "Classic Kerala Kasavu Saree Draping Tutorial",
                    "description": "Step by step kasavu saree draping with matching gold jewelry.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c",
                    "simulated_engagement": 41600,
                    "product_ids": [16, 28]
                }
            ]
        },
        {
            "id": 5,
            "name": "Fort Kochi Style",
            "youtube_url": "https://youtube.com/fort_kochi",
            "demographic": "gen-z",
            "subscriber_count": 500000,
            "subscriber_weight": 1.5,
            "vector": generate_vector("Gen-Z linen cotton summer coastal fashion modern artsy"),
            "videos": [
                {
                    "id": 106,
                    "video_url": "https://youtube.com/watch?v=kochi_linen_1",
                    "title": "Sustainable Linen Fits for Hot Kochi Summers",
                    "description": "Lookbook for Fort Kochi biennale showing off breezy sustainable linen.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b",
                    "simulated_engagement": 75000,
                    "product_ids": [92]
                }
            ]
        }
    ],
    "752001": [
        {
            "id": 6,
            "name": "Odisha Handloom Vlog",
            "youtube_url": "https://youtube.com/odisha_handloom",
            "demographic": "millennial",
            "subscriber_count": 95000,
            "subscriber_weight": 1.2,
            "vector": generate_vector("Millennial traditional cotton saree Sambalpuri Ikat handloom ethnic Odisha"),
            "videos": [
                {
                    "id": 107,
                    "video_url": "https://youtube.com/watch?v=puri_ikat_1",
                    "title": "Gorgeous Sambalpuri Ikat Sarees Collection",
                    "description": "Traditional Odia handloom silk and cotton sarees direct from local weavers.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b",
                    "simulated_engagement": 11400,
                    "product_ids": [31, 37]
                }
            ]
        },
        {
            "id": 7,
            "name": "Puri Style Hub",
            "youtube_url": "https://youtube.com/puri_style",
            "demographic": "gen-z",
            "subscriber_count": 120000,
            "subscriber_weight": 1.4,
            "vector": generate_vector("Gen-Z trendy casual cotton ethnic fusion affordable Odisha temple town"),
            "videos": [
                {
                    "id": 108,
                    "video_url": "https://youtube.com/watch?v=puri_fusion_1",
                    "title": "Odisha Temple Town Fusion Wear Styling",
                    "description": "Styling traditional block-prints and Pipli work applique in casual modern ways.",
                    "video_screenshot_url": "https://images.unsplash.com/photo-1617137968427-85924c800a22",
                    "simulated_engagement": 16800,
                    "product_ids": [37]
                }
            ]
        }
    ]
}

# Fallback Stores
FALLBACK_STORES = {
    "800008": [
        {"name": "Kalyan Silks Patna", "rating": 4.6, "review_count": 1200, "estimated_cost": 2500, "vector": generate_vector("traditional silk saree festive ethnic heavy embroidered Patna bridal")},
        {"name": "Manyavar Patna", "rating": 4.3, "review_count": 800, "estimated_cost": 3000, "vector": generate_vector("festive ethnic kurta set velvet silk wedding occasion Patna")},
        {"name": "Patna Fashion House", "rating": 4.1, "review_count": 350, "estimated_cost": 1500, "vector": generate_vector("affordable ethnic casual cotton kurti daily wear Patna budget")},
    ],
    "682001": [
        {"name": "Kochi Silk House", "rating": 4.5, "review_count": 600, "estimated_cost": 2800, "vector": generate_vector("South Indian silk saree traditional Kochi elegant Kanjeevaram Kasavu")},
        {"name": "Modern Trends Kochi", "rating": 4.0, "review_count": 200, "estimated_cost": 1800, "vector": generate_vector("modern fusion ethnic casual daily wear affordable Kochi trendy")},
        {"name": "Coastal Chic Boutique", "rating": 4.7, "review_count": 90, "estimated_cost": 2200, "vector": generate_vector("breezy coastal cotton rayon casual western beach Fort Kochi summer")},
    ],
    "752001": [
        {"name": "Boyanika Odisha Handlooms", "rating": 4.7, "review_count": 950, "estimated_cost": 2000, "vector": generate_vector("traditional Sambalpuri cotton saree handloom Ikat Puri Odisha")},
        {"name": "Priyadarshini Handlooms", "rating": 4.5, "review_count": 400, "estimated_cost": 2800, "vector": generate_vector("premium traditional tussar silk Sambalpuri saree elegant Odisha")},
        {"name": "Puri Jagannath Weaves", "rating": 4.3, "review_count": 150, "estimated_cost": 1500, "vector": generate_vector("affordable cotton saree dhoti local traditional weave Puri budget")},
    ]
}

# In-memory user session state
user_session = {
    "zip_code": "800008",
    "aesthetic": "casual",
    "aesthetic_vector": generate_vector("casual"),
    "age_group": "gen-z",
    "state": "discovery",
    "session_cart": [],
    "interactions": [],
    "time_offset_hours": 0,
    "date": "2026-08-15"
}

# Helper to map ZIP codes
def map_zip_code(zip_code: str) -> str:
    return ZIP_MAPPING.get(zip_code, zip_code)

def get_vibe_vector(vibe_name: str):
    vec = np.zeros(512)
    tags = {vibe_name}
    
    if any(t in tags for t in ["ethnic", "festive", "saree", "lehenga", "traditional", "jainsem", "jymphong", "mundu", "sherwani"]):
        vec[0:100] = 1.0
    if any(t in tags for t in ["casual", "summer", "linen", "cotton", "breathable"]):
        vec[100:200] = 1.0
    if any(t in tags for t in ["winter", "heavy-weight", "velvet", "shawl", "warm", "jacket", "cardigan", "woolen"]):
        vec[200:300] = 1.0
    if any(t in tags for t in ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party"]):
        vec[300:400] = 1.0
        
    vec[400:512] = 0.2
    
    hash_seed = abs(hash(vibe_name)) % (2**32)
    rng = np.random.default_rng(hash_seed)
    noise = rng.normal(0, 0.05, 512)
    vec += noise
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
        
    return vec.tolist()

# Load local catalog for fallback and validation
def load_fallback_catalog():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        return []
    try:
        with open(LOCAL_CATALOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read local catalog: {e}")
        return []

RAW_CATALOG = load_fallback_catalog()

# Initialize the PinPulseEngine instance
engine = PinPulseEngine(
    product_catalog=[],
    zip_data={
        "800008": {"city": "Patna", "state": "Bihar", "weather_conditions": "hot_humid", "aov": 1800},
        "682001": {"city": "Kochi", "state": "Kerala", "weather_conditions": "hot_humid", "aov": 2200},
        "752001": {"city": "Puri", "state": "Odisha", "weather_conditions": "warm_moderate", "aov": 1500},
    },
    festival_rules=FESTIVAL_RULES,
    weather_rules=WEATHER_RULES,
    creators=FALLBACK_CREATORS,
    stores=FALLBACK_STORES,
    cf_lookup=CF_LOOKUP
)

# Pydantic models for Dev Panel payloads
class CartPayload(BaseModel):
    item_id: int

class WishlistPayload(BaseModel):
    item_id: int

class StatePayload(BaseModel):
    state: str

class ZipPayload(BaseModel):
    zip_code: str

class TimeWarpPayload(BaseModel):
    hours: int

class FestivalPayload(BaseModel):
    festival: str = None

# Query Helper Functions (fetching from Supabase if connected)
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        try:
            from supabase import create_client
            return create_client(url, key)
        except Exception as e:
            logger.error(f"Error creating Supabase client: {e}")
    return None

def get_creators_data(zip_code):
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("creators").select("*").eq("zip_code", zip_code).execute()
            if res.data:
                creators = []
                for row in res.data:
                    creator = dict(row)
                    # Resolve vector/embedding field names to match expectation
                    if "embedding" in creator and creator["embedding"]:
                        creator["vector"] = creator["embedding"]
                    # Fetch videos for this creator
                    try:
                        v_res = sb.table("creator_videos").select("*").eq("creator_id", creator["id"]).execute()
                        creator["videos"] = []
                        if v_res.data:
                            for v_row in v_res.data:
                                video = dict(v_row)
                                # Fetch mapped product IDs for this video
                                try:
                                    p_res = sb.table("creator_video_products").select("product_id").eq("video_id", video["id"]).execute()
                                    video["product_ids"] = [p["product_id"] for p in p_res.data] if p_res.data else []
                                except Exception:
                                    video["product_ids"] = []
                                creator["videos"].append(video)
                    except Exception:
                        creator["videos"] = []
                    creators.append(creator)
                return creators
        except Exception as e:
            logger.error(f"Supabase creators query failed: {e}")
    return FALLBACK_CREATORS.get(zip_code, [])

def get_stores_data(zip_code):
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("stores").select("*").eq("zip_code", zip_code).execute()
            if res.data:
                return res.data
        except Exception as e:
            logger.error(f"Supabase stores query failed: {e}")
    return FALLBACK_STORES.get(zip_code, [])

def get_velocity_map(zip_code):
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("checkout_velocity").select("product_id, velocity_score, units_last_hour").eq("zip_code", zip_code).execute()
            if res.data:
                return {row["product_id"]: row for row in res.data}
        except Exception as e:
            logger.error(f"Supabase velocity fetch failed: {e}")
    # Local mock velocity mapping fallback
    from app.config import LOW_STOCK_THRESHOLD
    # Extract from LOCAL_VELOCITY_CACHE mock definitions
    from App_backup import LOCAL_VELOCITY_CACHE  # try fallback if available
    # programmatically mock velocity values
    mock_velocity = {
        1: {"velocity_score": 0.92, "units_last_hour": 47},
        2: {"velocity_score": 0.88, "units_last_hour": 38},
        7: {"velocity_score": 0.75, "units_last_hour": 22},
        9: {"velocity_score": 0.65, "units_last_hour": 18},
        16: {"velocity_score": 0.95, "units_last_hour": 52},
        31: {"velocity_score": 0.90, "units_last_hour": 42},
    }
    return mock_velocity

def get_db_products():
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("products").select("*").execute()
            if res.data:
                return res.data
        except Exception as e:
            logger.error(f"Supabase products fetch failed: {e}")
    return RAW_CATALOG

def get_active_event(zip_code, date_str):
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("calendar").select("*").eq("zip_code", zip_code).eq("date", date_str).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            logger.error(f"Supabase calendar query failed: {e}")
    return FALLBACK_CALENDAR.get((zip_code, date_str), {})

def enrich_product(p, velocity_map):
    p_tags = p.get("tags", [])
    p_id = p.get("id")
    desc_lower = p.get("description", "").lower()
    
    # 1. Determine material
    material = "cotton"
    for m in ["silk", "linen", "rayon", "velvet", "wool", "denim", "polyester", "chanderi", "georgette", "organza"]:
        if m in p_tags or m in desc_lower:
            material = m
            break
            
    # 2. Determine color
    color = "multi"
    for c in ["red", "maroon", "yellow", "gold", "white", "pink", "blue", "magenta", "saffron", "fuchsia", "black", "green"]:
        if c in p_tags or c in desc_lower:
            color = c
            break
            
    # 3. Determine nature
    nature = "casual"
    for n in ["ethnic", "festive", "casual", "streetwear", "traditional", "ceremonial"]:
        if n in p_tags or n in desc_lower:
            nature = n
            break
            
    # 4. Determine category
    category = "Ethnic"
    for cat in ["Ethnic", "Western", "Accessory", "Footwear"]:
        if cat.lower() in p_tags or cat.lower() in desc_lower:
            category = cat
            break
    if category == "Ethnic" and any(x in p_tags for x in ["hoodie", "cargo", "jeans", "jacket"]):
        category = "Western"
    if any(x in p_tags for x in ["earring", "necklace", "anklet", "ring", "sunglasses", "stole"]):
        category = "Accessory"
    if any(x in p_tags for x in ["boots", "mojari", "sandals", "footwear"]):
        category = "Footwear"

    # 5. Determine price
    price = (p_id * 17) % 3000 + 499
    
    # 6. Determine stock_level
    stock_level = (p_id * 7) % 50 + 1
    
    # 7. Determine is_evergreen
    is_evergreen = (p_id % 15 == 0)
    
    # 8. Determine baseline sales
    baseline_sales = (p_id * 3) % 20 + 5
    
    # 9. Determine current sales
    v_entry = velocity_map.get(p_id, velocity_map.get(str(p_id), {}))
    v_score = v_entry.get("velocity_score", 0.0)
    if v_score > 0:
        current_sales = int(baseline_sales * (1.0 + 2.0 * v_score))
    else:
        current_sales = baseline_sales + (p_id % 5)
        
    # 10. Determine age group
    age_group = "gen-z" if "streetwear" in p_tags or "modern" in p_tags or "gen-z" in p_tags else "millennial"
    
    # 11. Extract vectors
    embedding = p.get("embedding", [])
    if isinstance(embedding, str):
        try:
            embedding = json.loads(embedding)
        except Exception:
            pass
            
    return {
        "id": p_id,
        "name": p.get("name"),
        "description": p.get("description"),
        "image_url": p.get("image_url"),
        "product_url": p.get("product_url"),
        "tags": p_tags,
        "zip_codes": p.get("zip_codes", []),
        "material": material,
        "color": color,
        "nature": nature,
        "category": category,
        "price": price,
        "stock_level": stock_level,
        "is_evergreen": is_evergreen,
        "baseline_sales": baseline_sales,
        "current_sales": current_sales,
        "age_group": age_group,
        "aesthetic_vector": embedding,
        "fabric_vector": embedding,
        "event_vector": embedding,
        "embedding": embedding
    }

# FastAPI Endpoints

@app.get("/api/calendar-presets")
def get_calendar_presets():
    """Exposes all seeded calendar events grouped by ZIP code for dynamic frontend dropdowns."""
    presets = {
        "800008": [],
        "682001": [],
        "752001": []
    }
    
    # Try fetching from Supabase first
    sb = get_supabase_client()
    events_list = []
    if sb:
        try:
            res = sb.table("calendar").select("*").execute()
            if res.data:
                events_list = res.data
        except Exception as e:
            logger.error(f"Error fetching calendar presets from Supabase: {e}")
            
    # Fallback to local JSON if DB is empty or fails
    if not events_list:
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "calendar_presets.json"))
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    events_list = json.load(f)
            except Exception as e:
                logger.error(f"Error reading local calendar fallback presets: {e}")

    # Build response structured by ZIP code
    for row in events_list:
        z = row.get("zip_code")
        if z in presets:
            # Format to match the frontend expectations
            try:
                dt_obj = datetime.strptime(row.get("date"), "%Y-%m-%d")
                formatted_label = f"{dt_obj.strftime('%b %d')} ({row.get('event_name')})"
            except:
                formatted_label = f"{row.get('date')} ({row.get('event_name')})"
                
            presets[z].append({
                "key": f"{z}_{row.get('date')}",
                "label": formatted_label,
                "dateStr": row.get("date"),
                "event": row.get("event_name"),
                "event_type": row.get("event_type", "festival"),
                "isFestive": row.get("is_festive", True),
                "trendingTags": row.get("attire_tags", [])
            })
            
    # Sort events within each ZIP by date
    for z in presets:
        try:
            presets[z] = sorted(presets[z], key=lambda x: x["dateStr"])
        except:
            pass
        
    return presets

@app.get("/api/weather-matrix")
def get_weather_matrix():
    """Exposes the climate profiles and allowable materials dynamically to the client."""
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "weather_presets.json"))
    if os.path.exists(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading weather_presets.json: {e}")
            
    # Baseline fallback if file doesn't exist yet
    # Note: convert keys to strings because JSON response expects string keys for JSON serialization
    serialized_weather = {}
    for z, months in WEATHER_MATRIX.items():
        serialized_weather[z] = {str(m): data for m, data in months.items()}
    return serialized_weather

@app.get("/api/system-state")
def get_system_state():
    supabase_configured = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    return {
        "status": "online",
        "database_connected": supabase_configured,
        "database_engine": "Supabase pgvector" if supabase_configured else "Local In-Memory Similarity Simulation",
        "session": user_session
    }

@app.get("/api/zip-insights")
def get_zip_insights(zip_code: str = Query(...), date: str = Query(...)):
    from datetime import datetime, timedelta
    mapped_zip = map_zip_code(zip_code)
    
    # 1. Fetch AOV
    aov = 1500  # default
    
    # Try local json cache first
    local_insights_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "zip_code_insights.json"))
    if os.path.exists(local_insights_file):
        try:
            with open(local_insights_file, "r") as f:
                data = json.load(f)
                if mapped_zip in data:
                    aov = data[mapped_zip]
        except Exception as e:
            logger.error(f"Error reading zip_code_insights.json: {e}")
            
    # Try Supabase if connected
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("zip_code_insights").select("average_order_value").eq("zip_code", mapped_zip).execute()
            if res.data and len(res.data) > 0:
                aov = res.data[0]["average_order_value"]
        except Exception as e:
            logger.error(f"Supabase AOV fetch failed: {e}")
            
    # 2. Fetch weather
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        month = dt.month
    except Exception:
        month = 8
        dt = datetime.now()
        
    weather_entry = WEATHER_MATRIX.get(mapped_zip, {}).get(month, {
        "desc": "Pleasant & Breezy 🍃", "temp": "22°C", "weather_conditions": "warm_moderate"
    })
    
    # 3. Fetch Current Event
    current_event = None
    if sb:
        try:
            res = sb.table("calendar").select("*").eq("zip_code", mapped_zip).eq("date", date).execute()
            if res.data:
                current_event = res.data[0]
        except Exception as e:
            logger.error(f"Supabase current calendar event fetch failed: {e}")
    if not current_event:
        fall_event = FALLBACK_CALENDAR.get((mapped_zip, date))
        if fall_event:
            current_event = {
                "event_name": fall_event["event_name"],
                "event_type": fall_event["event_type"],
                "is_festive": fall_event["is_festive"]
            }

    # 4. Fetch Next 7 Days Events
    upcoming_events = []
    try:
        start_date = dt
        end_date = start_date + timedelta(days=7)
        
        if sb:
            try:
                res = sb.table("calendar") \
                    .select("*") \
                    .eq("zip_code", mapped_zip) \
                    .gte("date", start_date.strftime("%Y-%m-%d")) \
                    .lte("date", end_date.strftime("%Y-%m-%d")) \
                    .execute()
                if res.data:
                    upcoming_events = res.data
            except Exception as e:
                logger.error(f"Supabase upcoming events fetch failed: {e}")
                
        if not upcoming_events:
            # Fallback scan calendar
            for (z, d_str), val in FALLBACK_CALENDAR.items():
                if z == mapped_zip:
                    try:
                        d_obj = datetime.strptime(d_str, "%Y-%m-%d")
                        if start_date <= d_obj <= end_date:
                            upcoming_events.append({
                                "zip_code": z,
                                "date": d_str,
                                "event_name": val["event_name"],
                                "event_type": val["event_type"],
                                "is_festive": val["is_festive"]
                            })
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Error calculating upcoming events: {e}")

    # Remove duplicates if any
    seen = set()
    unique_upcoming = []
    for ev in upcoming_events:
        key = ev.get("date")
        if key not in seen:
            seen.add(key)
            # Standardize date format to string
            if hasattr(key, "isoformat"):
                ev["date"] = key.isoformat()
            elif isinstance(key, datetime):
                ev["date"] = key.strftime("%Y-%m-%d")
            unique_upcoming.append(ev)

    # Sort upcoming events chronologically
    unique_upcoming.sort(key=lambda x: str(x.get("date")))

    return {
        "zip_code": mapped_zip,
        "average_order_value": aov,
        "weather": weather_entry,
        "current_event": current_event,
        "upcoming_events": unique_upcoming
    }

@app.get("/api/products")
@app.get("/api/feed")
def get_feed(
    zip_code: str = Query(None),
    vibe: str = Query(None),
    date: str = Query(None),
    state: str = Query(None)
):
    """Unified feed generator executing the 8-pillar PinPulse math algorithm."""
    # Synchronize context values from parameters to user session
    if zip_code:
        user_session["zip_code"] = map_zip_code(zip_code)
    if vibe:
        user_session["aesthetic"] = vibe
        user_session["aesthetic_vector"] = get_vibe_vector(vibe)
    if state:
        user_session["state"] = state
    if date:
        user_session["date"] = date

    mapped_zip = user_session["zip_code"]
    active_date = user_session["date"]

    # Retrieve components
    creators = get_creators_data(mapped_zip)
    stores = get_stores_data(mapped_zip)
    velocity_map = get_velocity_map(mapped_zip)
    raw_products = get_db_products()
    active_event = get_active_event(mapped_zip, active_date)

    # Determine weather
    try:
        dt = datetime.strptime(active_date, "%Y-%m-%d")
        month = dt.month
    except Exception:
        month = 8

    weather_entry = WEATHER_MATRIX.get(mapped_zip, {}).get(month, {})
    weather_cond = weather_entry.get("weather_conditions", "hot_humid")

    # Populate engine objects dynamically
    engine.product_catalog = [enrich_product(p, velocity_map) for p in raw_products]
    engine.creators[mapped_zip] = creators
    engine.stores[mapped_zip] = stores

    # Fetch upcoming events in the next 7 days for priority scoring
    upcoming_events_data = []
    try:
        from datetime import timedelta
        if not isinstance(dt, datetime):
            dt = datetime.now()
        end_date = dt + timedelta(days=7)
        sb = get_supabase_client()
        if sb:
            res = sb.table("calendar") \
                .select("*") \
                .eq("zip_code", mapped_zip) \
                .gte("date", active_date) \
                .lte("date", end_date.strftime("%Y-%m-%d")) \
                .execute()
            if res.data:
                upcoming_events_data = res.data
        if not upcoming_events_data:
            # Fallback to in-memory calendar
            for (z, d_str), val in FALLBACK_CALENDAR.items():
                if z == mapped_zip:
                    try:
                        d_obj = datetime.strptime(d_str, "%Y-%m-%d")
                        if dt <= d_obj <= end_date:
                            upcoming_events_data.append({
                                "zip_code": z, "date": d_str,
                                "event_name": val["event_name"],
                                "event_type": val["event_type"],
                                "attire_tags": val.get("attire_tags", []),
                                "is_festive": val.get("is_festive", True)
                            })
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Error fetching upcoming events for engine: {e}")

    user_context = {
        "zip_code": mapped_zip,
        "aesthetic": user_session["aesthetic"],
        "aesthetic_vector": user_session["aesthetic_vector"],
        "age_group": user_session["age_group"],
        "state": user_session["state"],
        "session_cart": user_session["session_cart"],
        "interactions": user_session["interactions"],
        "time_offset_hours": user_session["time_offset_hours"],
        "weather_condition": weather_cond,
        "active_festival": active_event.get("event_name") if active_event and active_event.get("is_festive") else None,
        "active_date": active_date,
        "upcoming_events": upcoming_events_data  # Next 7 days — scored at 1.5x priority
    }

    scored = engine.score_all_products(user_context)

    # Re-map results to match front-end UI parameters and expectations
    formatted_products = []
    for item in scored:
        clean_item = {k: v for k, v in item.items() if not k.endswith("_vector") and k != "embedding"}
        
        weights = CONTEXT_MATRICES.get(user_session["state"], CONTEXT_MATRICES["discovery"])
        
        # Calculate overlapping active tags
        event_attire_tags = active_event.get("attire_tags", [])
        overlap_tags = [t for t in clean_item["tags"] if t in event_attire_tags]

        formatted_products.append({
            "id": clean_item["id"],
            "name": clean_item["name"],
            "description": clean_item["description"],
            "image_url": clean_item["image_url"],
            "product_url": clean_item.get("product_url"),
            "tags": clean_item["tags"],
            "zip_codes": clean_item.get("zip_codes", []),
            "vector_score": clean_item["s_aesthetic"],
            "tag_score": clean_item["s_creator"],
            "boost_score": clean_item["s_festivity"],
            "velocity_score": clean_item["s_velocity"],
            "velocity_boost": clean_item["s_intent"],
            "units_last_hour": clean_item["current_sales"] - clean_item["baseline_sales"],
            "is_trending": clean_item["s_velocity"] >= 0.75,
            "final_score": clean_item["final_score"],
            "overlap_tags": overlap_tags,
            "stock_level": clean_item.get("stock_level", 50),
            
            "scoring_breakdown": {
                "layer1_personal_vibe": round(weights["w_aesthetic"] * clean_item["s_aesthetic"], 4),
                "layer2_creator_trend": round(weights["w_creator"] * clean_item["s_creator"], 4),
                "layer3_local_boutique": round(weights["w_boutique"] * clean_item["s_boutique"], 4),
                "layer4_festivity": round(weights["w_festivity"] * clean_item["s_festivity"], 4),
                "layer5_weather": round(weights["w_fabric"] * clean_item["s_fabric"], 4),
                "layer6_velocity": round(weights["w_velocity"] * clean_item["s_velocity"], 4),
                "layer7_intent": round(weights["w_intent"] * clean_item["s_intent"], 4),
                "layer8_cf": round(weights["w_cf"] * clean_item["s_cf"], 4),
                "raw_values": {
                    "personal_vibe_similarity": clean_item["s_aesthetic"],
                    "creator_trend_match": clean_item["s_creator"],
                    "local_boutique_match": clean_item["s_boutique"],
                    "festivity_match": clean_item["s_festivity"],
                    "weather_match": clean_item["s_fabric"],
                    "checkout_velocity_score": clean_item["s_velocity"],
                    "intent_score": clean_item["s_intent"],
                    "cf_score": clean_item["s_cf"]
                }
            },
            "reason_labels": clean_item["reason_labels"]
        })

    return formatted_products

@app.get("/api/product/{product_id}")
def get_product(product_id: int):
    """PDP product details and collaborative filtering co-purchase shelf."""
    raw_products = get_db_products()
    product = next((p for p in raw_products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    enriched_p = enrich_product(product, {})
    
    # Calculate recommendations
    pdp_recs = engine.get_pdp_recommendations(product_id)
    
    # Clean vectors
    clean_product = {k: v for k, v in enriched_p.items() if not k.endswith("_vector") and k != "embedding"}
    clean_recs = []
    for r in pdp_recs:
        clean_r = {k: v for k, v in r.items() if not k.endswith("_vector") and k != "embedding"}
        clean_recs.append(clean_r)

    return {
        "product": clean_product,
        "also_bought": clean_recs
    }

@app.post("/api/cart/add")
def add_to_cart(payload: CartPayload):
    item_id = payload.item_id
    if item_id not in user_session["session_cart"]:
        user_session["session_cart"].append(item_id)
        user_session["interactions"].append({
            "item_id": item_id,
            "action_type": "cart",
            "hours_elapsed": 0,
        })
        user_session["state"] = "high_intent"
    return {
        "cart": user_session["session_cart"],
        "state": user_session["state"]
    }

@app.post("/api/cart/remove")
def remove_from_cart(payload: CartPayload):
    item_id = payload.item_id
    if item_id in user_session["session_cart"]:
        user_session["session_cart"].remove(item_id)
    if not user_session["session_cart"]:
        user_session["state"] = "discovery"
    return {
        "cart": user_session["session_cart"],
        "state": user_session["state"]
    }

@app.post("/api/wishlist/add")
def add_to_wishlist(payload: WishlistPayload):
    item_id = payload.item_id
    user_session["interactions"].append({
        "item_id": item_id,
        "action_type": "wishlist",
        "hours_elapsed": 0
    })
    return {"status": "wishlisted", "item_id": item_id}

# Dev Panel Endpoints

@app.get("/api/dev/state")
def get_dev_state():
    return {
        "session": user_session,
        "available_states": list(CONTEXT_MATRICES.keys()),
        "available_zips": ["800001", "560034", "752001"],
        "current_weights": CONTEXT_MATRICES.get(user_session["state"], {})
    }

@app.post("/api/dev/set-state")
def set_state(payload: StatePayload):
    new_state = payload.state
    if new_state in CONTEXT_MATRICES:
        user_session["state"] = new_state
    return {"state": user_session["state"]}

@app.post("/api/dev/set-zip")
def set_zip(payload: ZipPayload):
    new_zip = map_zip_code(payload.zip_code)
    user_session["zip_code"] = new_zip
    engine._cache = {}
    
    # Auto-adjust aesthetic based on region defaults
    if new_zip == "752001":
        user_session["aesthetic"] = "festive"
    else:
        user_session["aesthetic"] = "casual"
    user_session["aesthetic_vector"] = get_vibe_vector(user_session["aesthetic"])
    
    return {
        "zip_code": payload.zip_code,
        "city": "Patna" if new_zip == "800008" else "Kochi" if new_zip == "682001" else "Odisha",
        "state": user_session["state"]
    }

@app.post("/api/dev/time-warp")
def time_warp(payload: TimeWarpPayload):
    hours_to_add = payload.hours
    user_session["time_offset_hours"] += hours_to_add
    for interaction in user_session["interactions"]:
        interaction["hours_elapsed"] = interaction.get("hours_elapsed", 0) + hours_to_add
    return {
        "time_offset_hours": user_session["time_offset_hours"],
        "message": f"Fast-forwarded {hours_to_add}h. Total offset: {user_session['time_offset_hours']}h"
    }

@app.post("/api/dev/velocity-surge")
def velocity_surge():
    result = engine.simulate_velocity_surge(user_session["zip_code"])
    clean_products = []
    for p in result["products"]:
        clean_p = {k: v for k, v in p.items() if not k.endswith("_vector") and k != "embedding"}
        clean_products.append(clean_p)
    return {
        "theme": result["theme"],
        "products": clean_products,
        "log": result["log"]
    }

@app.post("/api/dev/set-festival")
def set_festival(payload: FestivalPayload):
    festival = payload.festival
    zip_code = user_session["zip_code"]
    
    if festival:
        user_session["state"] = "festive_season"
        # Temporarily inject active festival overrides
        user_session["active_festival"] = festival
    else:
        user_session["state"] = "discovery"
        user_session["active_festival"] = None
        
    engine._cache = {}
    return {
        "zip_code": zip_code,
        "festival": festival,
        "state": user_session["state"]
    }

@app.post("/api/dev/reset")
def reset_session():
    user_session.update({
        "zip_code": "800008",
        "aesthetic": "casual",
        "aesthetic_vector": get_vibe_vector("casual"),
        "age_group": "gen-z",
        "state": "discovery",
        "session_cart": [],
        "interactions": [],
        "time_offset_hours": 0,
        "date": "2026-08-15"
    })
    user_session.pop("active_festival", None)
    engine._cache = {}
    return {"status": "reset", "session": user_session}

# Fallback queries
try:
    from youtube_scraper import get_youtube_trend_match
except ModuleNotFoundError:
    from app.youtube_scraper import get_youtube_trend_match

@app.get("/api/trends/youtube")
def get_youtube_trends(zip_code: str):
    try:
        return get_youtube_trend_match(zip_code)
    except Exception as e:
        logger.error(f"YouTube scraper error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends/boutiques")
def get_boutiques_endpoint(zip_code: str):
    # Query stores data
    mapped_zip = map_zip_code(zip_code)
    stores = get_stores_data(mapped_zip)
    
    # Enrichment
    enriched_boutiques = []
    for idx, s in enumerate(stores):
        name = s["name"]
        rating = s.get("rating", 4.3)
        review_count = s.get("review_count", 200)
        cost = s.get("estimated_cost", 1500)
        
        # Address mock
        address = f"Shop {10 + idx}, Commercial Zone, {ZIP_MAPPING.get(zip_code, 'Local District')}"
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(f"{name} {zip_code}")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        
        # Match product
        matched_product = None
        for p in RAW_CATALOG:
            if idx % 3 == 0 and "festive" in p.get("tags", []):
                matched_product = p
                break
        if not matched_product and RAW_CATALOG:
            matched_product = RAW_CATALOG[idx % len(RAW_CATALOG)]
            
        enriched_boutiques.append({
            "store_id": f"STR_{zip_code}_{idx}",
            "zip_code": zip_code,
            "store_name": name,
            "rating": rating,
            "review_count": review_count,
            "estimated_cost": cost,
            "address": address,
            "maps_url": maps_url,
            "social_signal_source": "Google Places",
            "simulated_engagement": review_count * 10,
            "extracted_visual_trend": "ethnic" if idx % 2 == 0 else "casual",
            "style_vibe_cluster": "Local Boutique Drapes",
            "matched_product": matched_product
        })
    return {"zip_code": zip_code, "boutiques": enriched_boutiques}

@app.get("/api/look-completer")
def get_look_completer(product_id: int, occasion_tag: str):
    raw_products = get_db_products()
    primary_product = next((p for p in raw_products if p["id"] == product_id), None)
    if not primary_product:
        return {"accessory": None, "footwear": None, "suggested_dress": None}

    def get_embedding(p):
        emb = p.get("embedding", [])
        if isinstance(emb, str):
            try:
                emb = json.loads(emb)
            except:
                pass
        return emb

    primary_vector = get_embedding(primary_product)
    if not primary_vector or len(primary_vector) != 512:
        primary_vector = [0.0] * 512

    # 1. Resolve Suggested Accessory dynamically using Vector Similarity
    acc_candidates = [
        p for p in raw_products 
        if p["id"] != product_id and (
            str(p.get("category")).lower() == "accessory" or 
            "accessories" in p.get("tags", []) or 
            any(x in p["name"].lower() or x in p.get("description", "").lower() for x in ["earring", "necklace", "anklet", "ring", "sunglasses", "tote", "handbag", "watch", "bangle", "bracelet", "stole", "scarf", "beanie", "chunri", "dupatta", "jewelry"])
        )
    ]
    accessory_item = None
    if acc_candidates:
        best_acc = max(acc_candidates, key=lambda p: cosine_similarity(primary_vector, get_embedding(p)))
        accessory_item = {
            "id": best_acc["id"],
            "name": best_acc["name"],
            "image_url": best_acc["image_url"],
            "product_url": best_acc.get("product_url")
        }

    # 2. Resolve Suggested Footwear dynamically using Vector Similarity
    foot_candidates = [
        p for p in raw_products 
        if p["id"] != product_id and (
            str(p.get("category")).lower() == "footwear" or 
            "footwear" in p.get("tags", []) or 
            any(x in p["name"].lower() or x in p.get("description", "").lower() for x in ["boot", "shoe", "sandal", "heel", "mojri", "sneaker"])
        )
    ]
    footwear_item = None
    if foot_candidates:
        best_foot = max(foot_candidates, key=lambda p: cosine_similarity(primary_vector, get_embedding(p)))
        footwear_item = {
            "id": best_foot["id"],
            "name": best_foot["name"],
            "image_url": best_foot["image_url"],
            "product_url": best_foot.get("product_url")
        }

    # 3. Resolve Similar Suggested Dress dynamically using Vector Similarity
    dress_candidates = [
        p for p in raw_products 
        if p["id"] != product_id and (
            str(p.get("category")).lower() not in ["accessory", "footwear"] and
            p.get("category") == primary_product.get("category")
        )
    ]
    suggested_dress_item = None
    if dress_candidates:
        best_dress = max(dress_candidates, key=lambda p: cosine_similarity(primary_vector, get_embedding(p)))
        suggested_dress_item = {
            "id": best_dress["id"],
            "name": best_dress["name"],
            "image_url": best_dress["image_url"],
            "product_url": best_dress.get("product_url")
        }

    return {
        "accessory": accessory_item,
        "footwear": footwear_item,
        "suggested_dress": suggested_dress_item
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
