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

from fastapi.staticfiles import StaticFiles

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static image paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_IMAGES_DIR = os.path.abspath(os.path.join(ROOT_DIR, "frontend", "public", "images"))
DOWNLOADED_IMAGES_DIR = os.path.abspath(os.path.join(ROOT_DIR, "downloaded_images"))

if os.path.exists(ROOT_DIR):
    app.mount("/outfits", StaticFiles(directory=ROOT_DIR), name="outfits")
if os.path.exists(FRONTEND_IMAGES_DIR):
    app.mount("/images", StaticFiles(directory=FRONTEND_IMAGES_DIR), name="images")
if os.path.exists(DOWNLOADED_IMAGES_DIR):
    app.mount("/downloaded_images", StaticFiles(directory=DOWNLOADED_IMAGES_DIR), name="downloaded_images")

# File paths
LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))

# ── Startup: build velocity map from pinpulse_mock_db.json ───────────────────
# For each seeder record with hybrid_score > 0, boost the matched catalog
# product's velocity signal so that calculate_velocity_score() reflects
# real creator trend strength instead of the static mock dict.
MOCK_DB_VELOCITY_MAP: dict = {}  # product_id (int) → {velocity_score, units_last_hour}
_MOCK_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pinpulse_mock_db.json"))
try:
    with open(_MOCK_DB_FILE, "r", encoding="utf-8") as _f:
        _mock_records = json.load(_f)
    for _rec in _mock_records:
        _pid  = _rec.get("matched_product_id")
        _hscore = float(_rec.get("hybrid_score", 0.0))
        if _pid is None or _hscore <= 0:
            continue
        try:
            _pid = int(_pid)
        except (ValueError, TypeError):
            pass
        # Take the max hybrid_score seen for each product across all creator records.
        # velocity_score ∈ [0, 1] directly from hybrid_score.
        # units_last_hour is a synthetic estimate: base 5 + score-proportional boost.
        _existing = MOCK_DB_VELOCITY_MAP.get(_pid, {"velocity_score": 0.0, "units_last_hour": 0})
        if _hscore > _existing["velocity_score"]:
            MOCK_DB_VELOCITY_MAP[_pid] = {
                "velocity_score":  round(_hscore, 4),
                "units_last_hour": max(1, int(_hscore * 50)),
            }
    logger.info(
        f"Loaded pinpulse_mock_db.json → velocity map for "
        f"{len(MOCK_DB_VELOCITY_MAP)} products from creator trends."
    )
except FileNotFoundError:
    logger.info("pinpulse_mock_db.json not found — velocity pillar will use static fallback.")
except Exception as _e:
    logger.warning(f"Could not build velocity map from mock DB: {_e}")

# Load pre-computed zero-latency database for ultra-fast instant responses
PRECOMPUTED_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "precomputed_feed_db.json"))
PRECOMPUTED_DB = {}
try:
    if os.path.exists(PRECOMPUTED_DB_FILE):
        with open(PRECOMPUTED_DB_FILE, "r", encoding="utf-8") as _f:
            PRECOMPUTED_DB = json.load(_f)
        logger.info(f"Loaded precomputed_feed_db.json into memory ({len(PRECOMPUTED_DB.get('feed', {}))} feed keys).")
except Exception as _e:
    logger.warning(f"Could not load precomputed_feed_db.json: {_e}")

# Import recommender engine components
import sys
sys.path.append(os.path.dirname(__file__))
from national_festivals import NATIONAL_FESTIVAL_DEFINITIONS
from casual_events import CASUAL_EVENT_DEFINITIONS
from patna_events import PATNA_EVENT_DEFINITIONS
from jaipur_events import JAIPUR_EVENT_DEFINITIONS
from shillong_events import SHILLONG_EVENT_DEFINITIONS
from puri_events import PURI_EVENT_DEFINITIONS
from kochi_events import KOCHI_EVENT_DEFINITIONS
from config import CONTEXT_MATRICES, INTENT_DECAY_CONFIG, CACHE_TTL_SECONDS
from scoring_engine import (
    cosine_similarity,
    normalize_cosine_score,
    calculate_aesthetic_score,
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
    ("800008", "2026-01-03"): {"event_name": "Prakash Parv (Patna Sahib Gurudwara)", "event_type": "festival", "attire_tags": ["traditional", "white", "blue", "saffron", "patna"], "is_festive": True},
    ("800008", "2026-01-14"): {"event_name": "Makar Sankranti Harvest Mela", "event_type": "festival", "attire_tags": ["ethnic", "casual", "cotton", "yellow", "dailywear"], "is_festive": True},
    ("800008", "2026-02-02"): {"event_name": "Saraswati Puja (Vasant Panchami)", "event_type": "festival", "attire_tags": ["saree", "kurta", "yellow", "ethnic"], "is_festive": True},
    ("800008", "2026-03-22"): {"event_name": "Bihar Diwas (Bihar Day)", "event_type": "festival", "attire_tags": ["saree", "salwar", "bhagalpuri_silk", "kurta", "dhoti", "nehru_jacket", "white", "cream", "patna"], "is_festive": True},
    ("800008", "2026-11-15"): {"event_name": "Chhath Puja (Sandhya Arghya)", "event_type": "festival", "attire_tags": ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath_puja"], "is_festive": True},
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
    ("752001", "2026-09-15"): {"event_name": "Nuakhai Agricultural Harvest Festival", "event_type": "festival", "attire_tags": ["sambalpuri", "handloom", "cotton", "traditional", "ethnic", "saree", "kurta", "odisha"], "is_festive": True},
    ("752001", "2026-12-20"): {"event_name": "Odisha Winter Wedding (Pheras)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "tussar_silk", "ceremonial", "sherwani", "crimson", "gold"], "is_festive": True},
    # Rajasthan (302001)
    ("302001", "2026-01-14"): {"event_name": "Jaipur International Kite Festival (Makar Sankranti)", "event_type": "festival", "attire_tags": ["cotton", "yellow", "block_print", "anarkali", "rajasthan"], "is_festive": True},
    ("302001", "2026-02-15"): {"event_name": "Jaisalmer Desert Festival", "event_type": "festival", "attire_tags": ["bandhani", "mirror_work", "choli", "ethnic", "desert"], "is_festive": True},
    ("302001", "2026-03-20"): {"event_name": "Jaipur Royal Elephant & Holi Festival", "event_type": "festival", "attire_tags": ["bright", "cotton", "gota_patti", "jaipur"], "is_festive": True},
    ("302001", "2026-04-04"): {"event_name": "Royal Gangaur Festival Procession", "event_type": "festival", "attire_tags": ["traditional", "gota_patti", "lehenga", "gold", "rajasthan"], "is_festive": True},
    ("302001", "2026-08-12"): {"event_name": "Swarn Teej Festival Jaipur", "event_type": "festival", "attire_tags": ["lehenga", "gota_patti", "green", "silk", "teej", "ethnic"], "is_festive": True},
    ("302001", "2026-10-20"): {"event_name": "Marwar Folk Music & Dance Festival Jodhpur", "event_type": "festival", "attire_tags": ["mirror_work", "bandhani", "angrakha", "ethnic"], "is_festive": True},
    ("302001", "2026-11-18"): {"event_name": "Pushkar Camel Fair & Cultural Night", "event_type": "festival", "attire_tags": ["pushkar", "angrakha", "silk", "handloom", "traditional"], "is_festive": True},
    # Shillong (793001)
    ("793001", "2026-01-14"): {"event_name": "Highland Winter Music Fest", "event_type": "festival", "attire_tags": ["woolen", "winter", "knitted", "cardigan", "shillong"], "is_festive": True},
    ("793001", "2026-04-10"): {"event_name": "Shad Suk Mynsiem (Khasi Thanksgiving Dance)", "event_type": "festival", "attire_tags": ["jainsem", "khasi", "silk", "traditional", "gold", "nongkrem"], "is_festive": True},
    ("793001", "2026-05-15"): {"event_name": "Shillong Pine Spring Gala", "event_type": "festival", "attire_tags": ["pastel", "linen", "boho", "casual", "shillong"], "is_festive": True},
    ("793001", "2026-11-10"): {"event_name": "Nongkrem Dance Festival (Smit)", "event_type": "festival", "attire_tags": ["khasi", "silk", "brocade", "traditional", "gold", "velvet"], "is_festive": True},
    ("793001", "2026-11-15"): {"event_name": "Wangala 100 Drums Garo Festival", "event_type": "festival", "attire_tags": ["garo", "dakmanda", "wangala", "beaded", "handloom", "tribal"], "is_festive": True},
    ("793001", "2026-11-22"): {"event_name": "Shillong Cherry Blossom Festival", "event_type": "festival", "attire_tags": ["cherry_blossom", "pastel", "floral", "chiffon", "gown", "indie"], "is_festive": True},
    ("793001", "2026-12-25"): {"event_name": "Shillong Grand Christmas Solstice", "event_type": "festival", "attire_tags": ["woolen", "velvet", "cardigan", "red", "cozy", "festive"], "is_festive": True}
}

import time

class SimpleCache:
    def __init__(self, ttl=60):
        self.ttl = ttl
        self.store = {}

    def get(self, key):
        if key in self.store:
            val, expiry = self.store[key]
            if time.time() < expiry:
                return val
            else:
                del self.store[key]
        return None

    def set(self, key, value):
        self.store[key] = (value, time.time() + self.ttl)

api_cache = SimpleCache(ttl=CACHE_TTL_SECONDS)

def generate_vector(seed_text):
    np.random.seed(hash(seed_text) % (2**32))
    vec = np.random.randn(512)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

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
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from embed_catalog import get_vibe_vector as embed_get_vibe_vector
    
    vibe_lower = vibe_name.lower() if vibe_name else ""
    
    # Map the display names/keys from frontend to corresponding tag sets for embedding parity
    mapping = {
        "heritage_traditionalist": ("Heritage Traditionalist", ["traditional", "silk", "heavy", "classic", "ethnic", "saree", "kanjeevaram", "banarasi", "zari", "gold", "temple", "mundu", "sherwani", "jainsem"]),
        "heritage traditionalist": ("Heritage Traditionalist", ["traditional", "silk", "heavy", "classic", "ethnic", "saree", "kanjeevaram", "banarasi", "zari", "gold", "temple", "mundu", "sherwani", "jainsem"]),
        "festive_glam": ("Festive Glam", ["festive", "bright", "red", "embellished", "celebration", "lehenga", "anarkali", "ceremonial", "heavy_silk", "maroon", "gold", "brocade", "embroidery"]),
        "festive glam": ("Festive Glam", ["festive", "bright", "red", "embellished", "celebration", "lehenga", "anarkali", "ceremonial", "heavy_silk", "maroon", "gold", "brocade", "embroidery"]),
        "indie_fusion": ("Indie Fusion (Desi Boho)", ["fusion", "cotton", "prints", "oxidized", "casual-ethnic", "block-print", "indigo", "kurta", "denim", "boho", "handblock", "ethnic"]),
        "indie fusion": ("Indie Fusion (Desi Boho)", ["fusion", "cotton", "prints", "oxidized", "casual-ethnic", "block-print", "indigo", "kurta", "denim", "boho", "handblock", "ethnic"]),
        "indie fusion (desi boho)": ("Indie Fusion (Desi Boho)", ["fusion", "cotton", "prints", "oxidized", "casual-ethnic", "block-print", "indigo", "kurta", "denim", "boho", "handblock", "ethnic"]),
        "high_street_rebel": ("High-Street Rebel", ["streetwear", "oversized", "edgy", "grunge", "layered", "cargo", "graphic", "hoodie", "denim", "modern", "rebel", "baggy"]),
        "high-street rebel": ("High-Street Rebel", ["streetwear", "oversized", "edgy", "grunge", "layered", "cargo", "graphic", "hoodie", "denim", "modern", "rebel", "baggy"]),
        "coastal_tropical": ("Coastal Tropical", ["breathable", "pastel", "floral", "linen", "coastal", "summer", "cotton", "light", "breezy", "sundress", "resort"]),
        "coastal tropical": ("Coastal Tropical", ["breathable", "pastel", "floral", "linen", "coastal", "summer", "cotton", "light", "breezy", "sundress", "resort"]),
        "winter_academia": ("Winter Academia", ["winter", "layered", "preppy", "knitwear", "smart-casual", "trench", "plaid", "woolen", "jacket", "cardigan", "warm", "shadowl", "velvet"]),
        "winter academia": ("Winter Academia", ["winter", "layered", "preppy", "knitwear", "smart-casual", "trench", "plaid", "woolen", "jacket", "cardigan", "warm", "shadowl", "velvet"]),
        "y2k_nostalgia": ("Y2K Nostalgia", ["y2k", "vibrant", "retro", "pop", "gen-z", "crop", "baggy", "bucket-hat", "synthetic", "colorful", "neon", "bold"]),
        "y2k nostalgia": ("Y2K Nostalgia", ["y2k", "vibrant", "retro", "pop", "gen-z", "crop", "baggy", "bucket-hat", "synthetic", "colorful", "neon", "bold"]),
        "minimalist_essentials": ("Minimalist Essentials", ["minimal", "neutral", "solid", "clean", "basic", "white", "beige", "black", "fitted", "structured"]),
        "minimalist essentials": ("Minimalist Essentials", ["minimal", "neutral", "solid", "clean", "basic", "white", "beige", "black", "fitted", "structured"]),
        "earthy_handloom": ("Earthy Handloom", ["handloom", "organic", "earthy", "comfortable", "khadi", "ochre", "olive", "sustainable", "natural", "artisanal"]),
        "earthy handloom": ("Earthy Handloom", ["handloom", "organic", "earthy", "comfortable", "khadi", "ochre", "olive", "sustainable", "natural", "artisanal"]),
        "urban_athleisure": ("Urban Athleisure", ["sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "ribbed", "athletic", "gym", "jogger"]),
        "urban athleisure": ("Urban Athleisure", ["sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "ribbed", "athletic", "gym", "jogger"]),
        # Legacy/fallback keys
        "festive": ("Festive Glam", ["ethnic", "festive", "traditional", "silk", "saree", "jainsem", "jymphong", "mundu", "sherwani"]),
        "casual": ("Coastal Tropical", ["casual", "summer", "cotton", "linen", "breathable", "dailywear"]),
        "winter": ("Winter Academia", ["winter", "warm", "heavy-weight", "velvet", "shadowl", "jacket", "cardigan", "woolen"]),
        "streetwear": ("High-Street Rebel", ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party"])
    }
    
    aesthetic_name, tags = mapping.get(vibe_lower, (vibe_name, [vibe_name]))
    return embed_get_vibe_vector(tags, category_str=vibe_name, aesthetic_str=aesthetic_name)

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
        "800008": {"city": "Patna", "state": "Bihar", "aov": 1800},
        "682001": {"city": "Kochi", "state": "Kerala", "aov": 2200},
        "752001": {"city": "Puri", "state": "Odisha", "aov": 1500},
        "793001": {"city": "Shillong", "state": "Meghalaya", "aov": 2100},
        "302001": {"city": "Jaipur", "state": "Rajasthan", "aov": 2400},
    },
    festival_rules=FESTIVAL_RULES,
    creators=FALLBACK_CREATORS,
    stores=FALLBACK_STORES,
    cf_lookup=CF_LOOKUP
)



@app.get("/api/national-festivals")
def get_national_festivals():
    """Return complete specifications and queries for the 6 National Festivals."""
    return NATIONAL_FESTIVAL_DEFINITIONS

@app.get("/api/casual-events")
def get_casual_events():
    """Return complete specifications and queries for the 3 Casual Academic Events."""
    return CASUAL_EVENT_DEFINITIONS

@app.get("/api/patna-events")
def get_patna_events():
    """Return hyper-specific vector breakdown and queries for 5 local Patna events."""
    return PATNA_EVENT_DEFINITIONS

@app.get("/api/jaipur-events")
def get_jaipur_events():
    """Return hyper-specific vector breakdown and queries for 8 local Jaipur/Rajasthan events."""
    return JAIPUR_EVENT_DEFINITIONS

@app.get("/api/shillong-events")
def get_shillong_events():
    """Return hyper-specific vector breakdown and queries for 6 local Shillong events."""
    return SHILLONG_EVENT_DEFINITIONS

@app.get("/api/puri-events")
def get_puri_events():
    """Return hyper-specific vector breakdown and queries for 5 local Puri/Odisha events."""
    return PURI_EVENT_DEFINITIONS

@app.get("/api/kochi-events")
def get_kochi_events():
    """Return hyper-specific vector breakdown and queries for 4 local Kochi/Kerala events."""
    return KOCHI_EVENT_DEFINITIONS

class CartPayload(BaseModel):
    item_id: int

class WishlistPayload(BaseModel):
    item_id: int

class BuyPayload(BaseModel):
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
    return FALLBACK_CREATORS.get(zip_code, [])

def get_stores_data(zip_code):
    return FALLBACK_STORES.get(zip_code, [])

def get_velocity_map(zip_code):
    cache_key = f"velocity_{zip_code}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    # ── Primary: use creator trend data from seeder mock DB ───────────────────
    # MOCK_DB_VELOCITY_MAP is pre-built at startup from pinpulse_mock_db.json.
    # It maps product_id → {velocity_score, units_last_hour} keyed by
    # max(hybrid_score) across all creator records for that product.
    # We don't filter by zip_code here because the mock DB already scoped
    # matches to the correct zip at seeding time.
    if MOCK_DB_VELOCITY_MAP:
        api_cache.set(cache_key, MOCK_DB_VELOCITY_MAP)
        return MOCK_DB_VELOCITY_MAP

    # ── Secondary: try Supabase live velocity table ───────────────────────────
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("checkout_velocity").select("product_id, velocity_score, units_last_hour").eq("zip_code", zip_code).execute()
            if res.data:
                result = {row["product_id"]: row for row in res.data}
                api_cache.set(cache_key, result)
                return result
        except Exception as e:
            logger.error(f"Supabase velocity fetch failed: {e}")

    # ── Tertiary: static fallback (demo floor) ────────────────────────────────
    mock_velocity = {
        1: {"velocity_score": 0.92, "units_last_hour": 47},
        2: {"velocity_score": 0.88, "units_last_hour": 38},
        7: {"velocity_score": 0.75, "units_last_hour": 22},
        9: {"velocity_score": 0.65, "units_last_hour": 18},
        16: {"velocity_score": 0.95, "units_last_hour": 52},
        31: {"velocity_score": 0.90, "units_last_hour": 42},
    }
    api_cache.set(cache_key, mock_velocity)
    return mock_velocity

def get_db_products():
    cache_key = "db_products"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached
    catalog = load_fallback_catalog()
    api_cache.set(cache_key, catalog)
    return catalog

def get_active_event(zip_code, date_str):
    cache_key = f"active_event_{zip_code}_{date_str}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("calendar").select("*").eq("zip_code", zip_code).eq("date", date_str).execute()
            if res.data:
                result = res.data[0]
                api_cache.set(cache_key, result)
                return result
        except Exception as e:
            logger.error(f"Supabase calendar query failed: {e}")
    fallback = FALLBACK_CALENDAR.get((zip_code, date_str), {})
    api_cache.set(cache_key, fallback)
    return fallback

def enrich_product(p, velocity_map):
    p_tags = list(p.get("tags", []))
    p_id = p.get("id")
    name_lower = (p.get("name") or "").lower()
    desc_lower = p.get("description", "").lower()
    img_url = p.get("image_url") or ""

    # Enrich Urban Athleisure tags if item is hoodie, sweatshirt, tracksuit, activewear
    if any(k in name_lower for k in ["hooded", "sweatshirt", "hoodie", "tracksuit", "athleisure", "jogger", "sneakers", "activewear", "pullover"]):
        ath_keywords = ["urban", "athleisure", "sporty", "activewear", "comfortable", "casual", "sneakers", "tracksuit", "hoodie", "sweatshirt", "gym", "jogger", "athletic"]
        for kw in ath_keywords:
            if kw not in p_tags:
                p_tags.append(kw)
        p["tags"] = p_tags
        p["category"] = "Urban Athleisure"
        p["nature"] = "Urban Athleisure"
    
    # 1. Determine material — prefer DB value
    material = p.get("material")
    if not material:
        material = "cotton"
        for m in ["silk", "linen", "rayon", "velvet", "wool", "denim", "polyester", "chanderi", "georgette", "organza"]:
            if m in p_tags or m in desc_lower:
                material = m
                break
            
    # 2. Determine color — prefer DB value
    color = p.get("color")
    if not color:
        color = "multi"
        for c in ["red", "maroon", "yellow", "gold", "white", "pink", "blue", "magenta", "saffron", "fuchsia", "black", "green"]:
            if c in p_tags or c in desc_lower:
                color = c
                break
            
    # 3. Determine nature — prefer DB value
    nature = p.get("nature")
    if not nature:
        nature = "casual"
        for n in ["ethnic", "festive", "casual", "streetwear", "traditional", "ceremonial"]:
            if n in p_tags or n in desc_lower:
                nature = n
                break
            
    # 4. Determine aesthetic (4 Myntra WeForShe Global Aesthetic categories)
    # ---------------------------------------------------------------
    AESTHETIC_TAG_MAP = {
        "The Universal Traditionalist": ["kurta", "palazzo", "dupatta", "anarkali", "churidar", "saree", "kurti", "pyjama", "nehru-jacket", "modi-jacket", "rayon", "cotton-blend", "georgette", "chanderi", "art-silk", "chiffon", "block-print", "paisley", "yoke", "foil-print", "ikat", "mustard", "maroon", "emerald", "rani-pink", "ivory"],
        "Dark Academia":            ["turtleneck", "plaid", "trousers", "trench", "button-down", "sweater-vest", "pleated-skirt", "blazer", "pinafore", "tweed", "heavy-wool", "corduroy", "linen", "leather", "houndstooth", "argyle", "herringbone", "forest-green", "charcoal", "chocolate-brown", "burgundy", "navy", "beige"],
        "Cottagecore":               ["puff-sleeve", "corset", "prairie-blouse", "tiered-skirt", "maxi-skirt", "cardigan", "slip-dress", "overalls", "pinafore", "peasant-blouse", "muslin", "linen", "chiffon", "lace", "crochet", "floral", "ditsy-floral", "gingham", "botanical", "toile", "sage-green", "dusty-rose", "butter-yellow", "lavender"],
        "Grunge / Alt":              ["band-tee", "distressed-jeans", "combat-boots", "slip-dress", "tights", "long-sleeve", "cargo", "biker-jacket", "ripped-shorts", "distressed-denim", "leather", "mesh", "heavy-cotton", "stripes", "tie-dye", "crimson", "charcoal", "burgundy", "neon-green", "black"]
    }

    category = p.get("category")
    if not category:
        # Score product against each aesthetic using tag overlap
        best_aesthetic = "Dark Academia"
        best_score = 0
        combined = set(p_tags) | set(desc_lower.split())
        for aesthetic, a_tags in AESTHETIC_TAG_MAP.items():
            score = sum(1 for t in a_tags if t in combined)
            if score > best_score:
                best_score = score
                best_aesthetic = aesthetic
                best_aesthetic = aesthetic
        category = best_aesthetic

    # 5. Determine price — prefer DB value; only fallback if null
    price = p.get("price")
    if price is None:
        price = (p_id * 17) % 3000 + 499
    
    
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
        
    # 10. Determine age group — prefer DB value (age_range); normalise to lowercase
    age_group = p.get("age_range") or p.get("age_group")
    if not age_group:
        age_group = "gen-z" if "streetwear" in p_tags or "modern" in p_tags or "gen-z" in p_tags else "millennial"
    # Normalise to lowercase with hyphen (e.g. 'Gen Z' -> 'gen-z', 'Millennial' -> 'millennial')
    age_group = str(age_group).lower().strip().replace(" ", "-")
    
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
        "is_evergreen": is_evergreen,
        "baseline_sales": baseline_sales,
        "current_sales": current_sales,
        "age_group": age_group,
        "aesthetic_vector": embedding,
        "fabric_vector": embedding,
        "event_vector": embedding
    }

FALLBACK_CALENDAR = {
    ("800008", "2026-11-08"): {"event_name": "Chhath Puja", "event_type": "festival", "attire_tags": ["traditional", "saree", "yellow", "ethnic", "cotton"], "is_festive": True},
    ("682001", "2026-09-05"): {"event_name": "Onam", "event_type": "festival", "attire_tags": ["kasavu", "gold", "cream", "traditional", "ethnic"], "is_festive": True},
    ("752001", "2026-06-15"): {"event_name": "Raja Parba", "event_type": "festival", "attire_tags": ["pastel", "cotton", "traditional", "ethnic"], "is_festive": True},
    ("302001", "2026-10-20"): {"event_name": "Diwali", "event_type": "festival", "attire_tags": ["silk", "maroon", "gold", "embellished", "festive"], "is_festive": True},
    ("793001", "2026-12-25"): {"event_name": "Shillong Grand Christmas Solstice", "event_type": "festival", "attire_tags": ["woolen", "velvet", "cardigan", "red", "cozy", "festive"], "is_festive": True}
}

from datetime import datetime, timedelta

def get_active_event(zip_code, active_date_str):
    """
    Finds the active festival event for a given ZIP code and active date string.
    Per user specification: A festival banner/event is active for a 14-day window:
    Starting 10 days BEFORE the main festival date, up to 3 days AFTER (T-10 to T+3).
    """
    if not active_date_str:
        return None

    try:
        active_dt = datetime.strptime(str(active_date_str), "%Y-%m-%d")
    except Exception:
        active_dt = datetime.now()

    mapped_zip = map_zip_code(zip_code)
    sb = get_supabase_client()
    all_events = []

    if sb:
        try:
            res = sb.table("calendar").select("*").eq("zip_code", mapped_zip).execute()
            if res.data:
                all_events = res.data
        except Exception as e:
            logger.error(f"Error fetching calendar events from Supabase: {e}")

    if not all_events:
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "calendar_presets.json"))
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    all_events = [e for e in json.load(f) if e.get("zip_code") == mapped_zip]
            except Exception as e:
                logger.error(f"Error loading calendar presets: {e}")

        if not all_events:
            for (z, d_str), val in FALLBACK_CALENDAR.items():
                if z == mapped_zip:
                    all_events.append({
                        "zip_code": z,
                        "date": d_str,
                        "event_name": val["event_name"],
                        "event_type": val.get("event_type", "festival"),
                        "attire_tags": val.get("attire_tags", []),
                        "is_festive": val.get("is_festive", True)
                    })

    matching_events = []
    for ev in all_events:
        try:
            ev_date_str = ev.get("date")
            if not ev_date_str:
                continue
            ev_dt = datetime.strptime(str(ev_date_str), "%Y-%m-%d")
            
            # 14-day active window: 10 days before event, 3 days after event
            start_window = ev_dt - timedelta(days=10)
            end_window = ev_dt + timedelta(days=3)

            if start_window <= active_dt <= end_window:
                distance = abs((ev_dt - active_dt).days)
                matching_events.append((distance, ev))
        except Exception:
            pass

    if matching_events:
        matching_events.sort(key=lambda x: x[0])
        return matching_events[0][1]

    return None

# FastAPI Endpoints

@app.get("/api/calendar-presets")
def get_calendar_presets():
    """Exposes all seeded calendar events grouped by ZIP code for dynamic frontend dropdowns."""
    cache_key = "calendar_presets"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

    presets = {
        "800008": [],
        "682001": [],
        "752001": [],
        "793001": [],
        "302001": []
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
        
    api_cache.set(cache_key, presets)
    return presets

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
    cache_key = f"zip_insights_{zip_code}_{date}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return cached

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
            
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except Exception:
        dt = datetime.now()
        
    # 2. Fetch Active Event
    current_event = get_active_event(mapped_zip, date)

    # 3. Fetch Next 7 Days Events
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

    res_val = {
        "zip_code": mapped_zip,
        "average_order_value": aov,
        "current_event": current_event,
        "upcoming_events": unique_upcoming
    }
    api_cache.set(cache_key, res_val)
    return res_val

@app.get("/api/products")
@app.get("/api/feed")
def get_feed(
    zip_code: str = Query(None),
    vibe: str = Query(None),
    date: str = Query(None),
    state: str = Query(None),
    gender: str = Query(None)  # 'women' | 'men' | 'kids'
):
    """Unified feed generator serving fast pre-computed, verified catalog recommendations."""
    mapped_zip = map_zip_code(zip_code) if zip_code else "800008"
    gender_norm = (gender or "women").lower().strip()
    if gender_norm in ("men", "male"):
        g_key = "men"
    elif gender_norm in ("kids", "children", "boys", "girls", "boy", "girl"):
        g_key = "kids"
    else:
        g_key = "women"

    feed_key = f"{mapped_zip}_{g_key}"
    if PRECOMPUTED_DB and "feed" in PRECOMPUTED_DB and feed_key in PRECOMPUTED_DB["feed"]:
        return PRECOMPUTED_DB["feed"][feed_key]

    # Fallback to local catalog if key missing
    all_products = get_db_products()
    return all_products[:30]

    # Fetch upcoming events in the next 7 days for priority scoring
    upcoming_events_data = []
    cache_key_events = f"upcoming_events_{mapped_zip}_{active_date}"
    cached_events = api_cache.get(cache_key_events)
    if cached_events is not None:
        upcoming_events_data = cached_events
    else:
        try:
            from datetime import timedelta, datetime as dt_cls
            dt_obj = datetime.strptime(active_date, "%Y-%m-%d") if active_date else dt_cls.now()
            end_date = dt_obj + timedelta(days=7)
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
                            d_o = datetime.strptime(d_str, "%Y-%m-%d")
                            if dt_obj <= d_o <= end_date:
                                upcoming_events_data.append({
                                    "zip_code": z, "date": d_str,
                                    "event_name": val["event_name"],
                                    "event_type": val["event_type"],
                                    "attire_tags": val.get("attire_tags", []),
                                    "is_festive": val.get("is_festive", True)
                                })
                        except Exception:
                            pass
            api_cache.set(cache_key_events, upcoming_events_data)
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
        "active_festival": active_event.get("event_name") if active_event and active_event.get("is_festive") else None,
        "active_date": active_date,
        "upcoming_events": upcoming_events_data  # Next 7 days — scored at 1.5x priority
    }

    scored = engine.score_all_products(user_context)

    # ── Strict Lingerie & Innerwear Filter ──────────────────
    lingerie_kw = [
        "bra", "bras", "panty", "panties", "briefs", "boxers", "lingerie", "innerwear",
        "thong", "pantyhose", "stockings", "bustier", "shapewear", "nightwear", "nightdress",
        "babydoll", "camisole", "bikini", "underwear", "swimwear", "thermal top", "thermal bottoms",
        "night-suits", "night suits", "pajamas", "pyjamas", "lounge shorts"
    ]
    scored = [
        item for item in scored
        if not any(kw in str(item.get("name", "")).lower() for kw in lingerie_kw) and
           not any(kw in str(item.get("category", "")).lower() for kw in lingerie_kw) and
           not any(kw in " ".join(item.get("tags", [])).lower() for kw in lingerie_kw)
    ]

    # ── Strict Festival Mode Filter: block modern athleisure/casual items ──
    is_festival_mode = (user_session.get("state") == "festive_season") or (active_event and active_event.get("is_festive"))
    if is_festival_mode:
        blocked_kw = ["hoodie", "sweatshirt", "tracksuit", "activewear", "sneakers", "crop", "miniskirt", "gym", "jogger"]
        scored = [
            item for item in scored 
            if not any(k in item.get("name", "").lower() for k in blocked_kw) and 
               not any(k in item.get("tags", []) for k in blocked_kw)
        ]

    # Re-map results to match front-end UI parameters and expectations
    formatted_products = []
    for item in scored:
        clean_item = {k: v for k, v in item.items() if not k.endswith("_vector") and k != "embedding"}
        
        weights = engine.get_context_matrix(user_session["state"], user_context)
        
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
            "price": clean_item.get("price"),
            "category": clean_item.get("category"),
            "vector_score": clean_item["s_aesthetic"],
            "tag_score": clean_item["s_creator"],
            "boost_score": clean_item["s_festivity"],
            "price_score": clean_item["s_price"],
            "final_score": clean_item["final_score"],
            "overlap_tags": overlap_tags,
            
            "scoring_breakdown": {
                "layer1_personal_vibe": round(weights["w_aesthetic"] * clean_item["s_aesthetic"], 4),
                "layer2_creator_trend": round(weights["w_creator"] * clean_item["s_creator"], 4),
                "layer3_local_boutique": round(weights["w_boutique"] * clean_item["s_boutique"], 4),
                "layer4_festivity": round(weights["w_festivity"] * clean_item["s_festivity"], 4),
                "layer5_price": round(clean_item["s_price"], 4),
                "raw_values": {
                    "personal_vibe_similarity": clean_item["s_aesthetic"],
                    "creator_trend_match": clean_item["s_creator"],
                    "local_boutique_match": clean_item["s_boutique"],
                    "festivity_match": clean_item["s_festivity"],
                    "price_affinity": clean_item["s_price"]
                }
            },
            "reason_labels": clean_item["reason_labels"]
        })

    # ── Deduplicate products to prevent identical items or image URLs appearing twice ──
    dedup_seen = set()
    unique_formatted = []
    for item in formatted_products:
        item_key = (str(item.get("name", "")).strip().lower(), str(item.get("image_url", "")).strip())
        if item_key not in dedup_seen:
            dedup_seen.add(item_key)
            unique_formatted.append(item)
    formatted_products = unique_formatted

    return formatted_products

@app.get("/api/product/{product_id}")
def get_product(product_id: int):
    """PDP product details and collaborative filtering co-purchase shelf."""
    raw_products = get_db_products()
    product = next((p for p in raw_products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Populate engine catalog to ensure recommendations can lookup products correctly
    engine.product_catalog = [enrich_product(p, {}) for p in raw_products]

    enriched_p = enrich_product(product, {})
    
    # Calculate recommendations safely
    try:
        pdp_recs = engine.get_pdp_recommendations(product_id)
    except Exception:
        pdp_recs = []
    
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

@app.post("/api/buy")
def buy_product(payload: BuyPayload):
    item_id = payload.item_id
    
    # 1. Add "buy" interaction to session interactions
    user_session["interactions"].append({
        "item_id": item_id,
        "action_type": "buy",
        "hours_elapsed": 0,
    })
    
    # 2. To dynamically increase local sales velocity, increment current_sales in DB
    sb = get_supabase_client()
    if sb:
        try:
            res = sb.table("products").select("id, current_sales").eq("id", item_id).execute()
            if res.data and len(res.data) > 0:
                # If current_sales is null or 0, default to 5
                curr = res.data[0].get("current_sales") or 5
                sb.table("products").update({"current_sales": curr + 1}).eq("id", item_id).execute()
                logger.info(f"Incremented current_sales for product ID {item_id} in Supabase.")
        except Exception as e:
            logger.error(f"Failed to record buy in Supabase: {e}")

    # Clear cache to force recalculation
    engine._cache = {}
    
    return {
        "status": "success",
        "message": f"Successfully purchased product {item_id}",
        "cart": user_session["session_cart"]
    }

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
        "city": engine.zip_data.get(new_zip, {}).get("city", "Patna"),
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
def get_youtube_trends(zip_code: str = Query("800008")):
    mapped_zip = map_zip_code(zip_code) if zip_code else "800008"
    if PRECOMPUTED_DB and "youtube_trends" in PRECOMPUTED_DB and mapped_zip in PRECOMPUTED_DB["youtube_trends"]:
        return PRECOMPUTED_DB["youtube_trends"][mapped_zip]
    try:
        return get_youtube_trend_match(mapped_zip)
    except Exception:
        return []

@app.get("/api/trends/boutiques")
def get_boutiques_endpoint(zip_code: str = Query("800008"), target_dresses: int = 25):
    mapped_zip = map_zip_code(zip_code) if zip_code else "800008"
    if PRECOMPUTED_DB and "boutique_trends" in PRECOMPUTED_DB and mapped_zip in PRECOMPUTED_DB["boutique_trends"]:
        return PRECOMPUTED_DB["boutique_trends"][mapped_zip]
    return {"zip_code": mapped_zip, "region_name": "Regional", "boutiques": []}
    mock_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pinpulse_mock_db.json"))
    if os.path.exists(mock_db_path):
        try:
            with open(mock_db_path, "r", encoding="utf-8") as f:
                mock_records = json.load(f)

            mock_boutiques = [r for r in mock_records if r.get("pincode") == zip_code and r.get("type") == "boutique"]
            if mock_boutiques:
                boutique_groups = {}
                for r in mock_boutiques:
                    store_name = r.get("store_name") or r.get("metadata", {}).get("store_name", "Unknown Store")
                    if store_name not in boutique_groups:
                        boutique_groups[store_name] = []
                    boutique_groups[store_name].append(r)

                for idx, (name, records) in enumerate(boutique_groups.items()):
                    rating = round(4.2 + (idx % 5) * 0.1, 1)
                    review_count = 120 + (idx % 8) * 45
                    cost = records[0].get("metadata", {}).get("estimated_price_inr", 1500)
                    address = f"Shop {10 + idx}, Commercial Zone, {ZIP_MAPPING.get(zip_code, 'Local District')}"
                    import urllib.parse
                    encoded_query = urllib.parse.quote_plus(f"{name} {zip_code}")
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

                    store_products = []
                    for r in records:
                        mp_id = r.get("matched_product_id")
                        score = r.get("hybrid_score", 0.0)

                        if not mp_id or mp_id not in catalog_map or score < 0.01:
                            catalog_gaps.append({
                                "store_name": name,
                                "zip_code": zip_code,
                                "trending_item": r.get("metadata", {}).get("item", "Boutique drape"),
                                "reason": "No matching product in Myntra catalog meeting similarity threshold"
                            })
                            continue

                        if mp_id not in used_product_ids and len(used_product_ids) < target_dresses:
                            used_product_ids.add(mp_id)
                            clean_p = {k: v for k, v in catalog_map[mp_id].items() if not k.endswith("_vector") and k != "embedding"}
                            store_products.append(clean_p)

                    trend_tags = [r.get("metadata", {}).get("aesthetic") for r in records if r.get("metadata", {}).get("aesthetic")]
                    extracted_trend = ", ".join(list(set(trend_tags))[:2]) if trend_tags else "ethnic"

                    # If store_products is empty, take first available match or top catalog match
                    matched_product = store_products[0] if store_products else None

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
                        "extracted_visual_trend": extracted_trend,
                        "style_vibe_cluster": "Local Boutique Drapes",
                        "matched_product": matched_product,
                        "store_dresses": store_products
                    })
        except Exception as e:
            logger.error(f"Error parsing mock DB boutiques: {e}")

    # 2. Fall back / complement with store data to hit 25 dresses overall per ZIP
    if len(used_product_ids) < target_dresses:
        for idx, s in enumerate(stores):
            name = s["name"]
            rating = s.get("rating", 4.3)
            review_count = s.get("review_count", 200)
            cost = s.get("estimated_cost", 1500)
            address = f"Shop {10 + idx}, Commercial Zone, {ZIP_MAPPING.get(zip_code, 'Local District')}"
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(f"{name} {zip_code}")
            maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

            store_vector = s.get("vector") or s.get("embedding")
            store_products = []

            # Rank catalog items by store vector similarity
            scored_p = []
            for p in catalog:
                pid = p.get("id")
                if pid in used_product_ids:
                    continue
                p_vec = p.get("embedding") or p.get("image_vector")
                if not p_vec or not store_vector:
                    continue
                score = normalize_cosine_score(cosine_similarity(store_vector, p_vec))
                scored_p.append((score, p))

            scored_p.sort(key=lambda x: -x[0])

            # Gather top matches for this boutique
            for score, best_p in scored_p:
                if len(used_product_ids) >= target_dresses or len(store_products) >= 10:
                    break

                if score < -100.0:
                    catalog_gaps.append({
                        "store_name": name,
                        "zip_code": zip_code,
                        "extracted_visual_trend": s.get("extracted_visual_trend", "ethnic"),
                        "reason": f"No catalog product reached minimum similarity threshold (best score: {score:.3f} < -100.0)"
                    })
                    break

                used_product_ids.add(best_p["id"])
                clean_p = {k: v for k, v in best_p.items() if not k.endswith("_vector") and k != "embedding"}
                store_products.append(clean_p)

            matched_product = store_products[0] if store_products else None

            # Only append store card if not already added from mock DB
            if not any(b["store_name"] == name for b in enriched_boutiques):
                enriched_boutiques.append({
                    "store_id": f"STR_{zip_code}_{len(enriched_boutiques)}",
                    "zip_code": zip_code,
                    "store_name": name,
                    "rating": rating,
                    "review_count": review_count,
                    "estimated_cost": cost,
                    "address": address,
                    "maps_url": maps_url,
                    "social_signal_source": "Google Places",
                    "simulated_engagement": review_count * 10,
                    "extracted_visual_trend": s.get("extracted_visual_trend", "ethnic" if idx % 2 == 0 else "casual"),
                    "style_vibe_cluster": "Local Boutique Drapes",
                    "matched_product": matched_product,
                    "store_dresses": store_products
                })

    # Collect all unique dresses across stores
    all_unique_dresses = []
    seen_d_ids = set()
    for b in enriched_boutiques:
        for d in (b.get("store_dresses") or []):
            if d["id"] not in seen_d_ids:
                seen_d_ids.add(d["id"])
                all_unique_dresses.append(d)
        if b.get("matched_product") and b["matched_product"]["id"] not in seen_d_ids:
            seen_d_ids.add(b["matched_product"]["id"])
            all_unique_dresses.append(b["matched_product"])

    res_val = {
        "zip_code": zip_code,
        "total_dresses": len(all_unique_dresses),
        "boutiques": enriched_boutiques,
        "dresses": all_unique_dresses,
        "catalog_gaps": catalog_gaps
    }
    api_cache.set(cache_key, res_val)
    return res_val


@app.get("/api/trends/global")
def get_global_trends(city: str = Query(None), top_k: int = Query(3)):
    """Returns Global Runway trend data with top-K matched catalog products per trend.
    Uses Jaccard tag-overlap similarity to match trends to catalog items.
    Optionally filter by city: 'tokyo', 'paris', 'seoul'.
    """
    if not GLOBAL_TRENDS_CACHE:
        return {"error": "Global trends cache not available.", "cities": []}

    cities_data = GLOBAL_TRENDS_CACHE.get("cities", {})
    meta = GLOBAL_TRENDS_CACHE.get("meta", {})

    # ── Load catalog for matching ──────────────────────────────────────────
    raw_products = get_db_products()

    def jaccard_tag_score(trend_tags: list, product_tags: list) -> float:
        """Jaccard similarity: |A ∩ B| / |A ∪ B|"""
        t = set(t.lower().strip() for t in trend_tags)
        p = set(t.lower().strip() for t in product_tags)
        if not t or not p:
            return 0.0
        intersection = len(t & p)
        union = len(t | p)
        return intersection / union if union > 0 else 0.0

    def find_top_matches(trend: dict, k: int = 3) -> list:
        """Score every catalog product against a trend, return top-K."""
        # Combine vibe_tags + matched_catalog_tags as the trend's tag fingerprint
        trend_tags = list(set(
            trend.get("vibe_tags", []) + trend.get("matched_catalog_tags", [])
        ))
        scored = []
        for p in raw_products:
            product_tags = p.get("tags", [])
            score = jaccard_tag_score(trend_tags, product_tags)
            if score > 0:
                # Count overlapping tags for display
                trend_tag_set = set(t.lower() for t in trend_tags)
                product_tag_set = set(t.lower() for t in product_tags)
                overlap = sorted(trend_tag_set & product_tag_set)
                scored.append((score, overlap, p))
        # Sort descending by score, take top-k
        scored.sort(key=lambda x: -x[0])
        results = []
        for score, overlap, p in scored[:k]:
            results.append({
                "id": p["id"],
                "name": p["name"],
                "image_url": p.get("image_url", ""),
                "price": p.get("price"),
                "product_url": p.get("product_url"),
                "category": p.get("category", ""),
                "tags": p.get("tags", []),
                "overlap_tags": overlap,
                "match_score": round(score, 4)
            })
        return results

    # ── Build enriched city data with matched products per trend ───────────
    if city and city.lower() in cities_data:
        filtered_keys = [city.lower()]
    else:
        filtered_keys = list(cities_data.keys())

    enriched_cities = {}
    for city_key in filtered_keys:
        city_block = cities_data[city_key]
        enriched_trends = []
        for trend in city_block.get("trends", []):
            enriched_trend = dict(trend)
            enriched_trend["matched_products"] = find_top_matches(trend, k=top_k)
            enriched_trends.append(enriched_trend)
        enriched_cities[city_key] = {**city_block, "trends": enriched_trends}

    return {
        "meta": meta,
        "cities": enriched_cities,
        "feed_injection_config": GLOBAL_TRENDS_CACHE.get("feed_injection_config", {})
    }


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

SEASON_DEFINITIONS = {
    "summer": {
        "title": "Summer Apparel & Resort Collection",
        "description": "Breathable cottons, linens, pastels, short sleeves, and light ethnic wear engineered for high temperatures.",
        "badge": "☀️ Summer Breeze",
        "icon": "☀️",
        "materials": ["cotton", "linen", "organza", "georgette", "rayon"],
        "keywords": ["short", "sleeveless", "pastel", "light", "breeze", "dress", "saree", "top", "co-ord", "skirt", "kurti", "yellow", "white", "pink", "sky blue"]
    },
    "winter": {
        "title": "Winter Wardrobe & Outerwear",
        "description": "Cozy knits, velvets, denim layers, Nehru sets, hoodies, and jackets to keep you warm and stylish.",
        "badge": "❄️ Winter Cozy",
        "icon": "❄️",
        "materials": ["velvet", "wool", "denim", "silk", "leather", "knit"],
        "keywords": ["jacket", "hoodie", "sweater", "coat", "sleeve", "cardigan", "nehru", "velvet", "black", "maroon", "navy", "layer"]
    },
    "monsoon": {
        "title": "Monsoon Streetwear & Quick-Dry Outfits",
        "description": "Vibrant, comfortable, easy-to-dry casuals, cropped fits, and light layers perfect for rainy weather.",
        "badge": "🌧️ Monsoon Rain-Ready",
        "icon": "🌧️",
        "materials": ["nylon", "polyester", "cotton", "denim", "synthetic"],
        "keywords": ["casual", "streetwear", "crop", "t-shirt", "shorts", "bomber", "teal", "olive", "activewear", "quick-dry"]
    },
    "autumn": {
        "title": "Autumn & Transitional Layers",
        "description": "Lightweight jackets, woolen cardigans, trench coats, sweaters, and denim layers engineered for crisp, breezy autumn weather.",
        "badge": "🍂 Autumn Layers",
        "icon": "🍂",
        "materials": ["wool", "denim", "cotton", "fleece", "leather", "knit"],
        "keywords": ["jacket", "coat", "trench", "sweater", "cardigan", "overcoat", "hoodie", "pullover", "layered", "transitional", "layer", "knitwear"]
    }
}

@app.get("/api/trends/seasonal")
def get_seasonal_trends(season: str = Query("summer")):
    """Returns curated apparel collections for the specified season ('summer', 'winter', 'monsoon', 'autumn')."""
    season_key = str(season).lower().strip()
    if season_key not in SEASON_DEFINITIONS:
        season_key = "summer"
    
    spec = SEASON_DEFINITIONS[season_key]
    raw_products = get_db_products()
    
    def score_seasonal_product(p):
        p_tags = [str(t).lower() for t in p.get("tags", [])]
        p_mat = str(p.get("material", "")).lower()
        p_desc = str(p.get("description", "")).lower()
        p_name = str(p.get("name", "")).lower()
        
        # Strict exclusion: for Autumn, exclude Sarees, Lehengas, Dupattas unless explicitly a transitional layer
        if season_key == "autumn":
            if any(k in p_name or k in p_tags for k in ["saree", "lehenga", "dupatta", "anklet", "payal", "necklace", "ring", "earring"]):
                return 0.0

        score = 0.0
        if p_mat in spec["materials"]:
            score += 2.0
        for kw in spec["keywords"]:
            if kw in p_tags or kw in p_desc or kw in p_name:
                score += 1.5
        return score

    scored_items = []
    for p in raw_products:
        if p.get("is_global_trend"):
            continue
        sc = score_seasonal_product(p)
        # Require positive match score >= 1.5 (zero un-matched fallback fillers)
        if sc >= 1.5:
            item_copy = dict(p)
            item_copy["season_badge"] = spec["badge"]
            item_copy["seasonal_score"] = round(sc, 2)
            scored_items.append((sc, item_copy))
    
    scored_items.sort(key=lambda x: x[0], reverse=True)
    matched_products = [item for _, item in scored_items[:30]]
    
    catalog_gap_note = None
    if len(matched_products) < 30:
        gap_count = 30 - len(matched_products)
        catalog_gap_note = f"Found {len(matched_products)} genuine {spec['title']} matching climate criteria. Catalog gap of {gap_count} items reported (zero random fallbacks inserted)."

    return {
        "season": season_key,
        "meta": spec,
        "products": matched_products,
        "total_matched": len(matched_products),
        "catalog_gap_note": catalog_gap_note
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

