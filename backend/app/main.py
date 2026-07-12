import os
import json
import logging
import numpy as np
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
TREND_CACHE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "youtube_cache.json"))

# Fallback calendar data when offline
FALLBACK_CALENDAR = {
    # Patna
    ("800008", "2026-11-11"): {"event_name": "Chitragupta Puja & Bhai Dooj", "event_type": "festival", "attire_tags": ["ethnic", "festive", "traditional", "pink", "red", "yellow"], "is_festive": True},
    ("800008", "2026-11-13"): {"event_name": "Chhath Puja (Nahay Khay)", "event_type": "festival", "attire_tags": ["cotton", "saree", "traditional", "yellow", "white", "patna"], "is_festive": True},
    ("800008", "2026-11-14"): {"event_name": "Chhath Puja (Kharna)", "event_type": "festival", "attire_tags": ["cotton", "saree", "traditional", "yellow", "white", "patna"], "is_festive": True},
    ("800008", "2026-11-15"): {"event_name": "Chhath Puja (Sandhya Arghya)", "event_type": "festival", "attire_tags": ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath-puja"], "is_festive": True},
    ("800008", "2026-11-16"): {"event_name": "Chhath Puja (Usha Arghya)", "event_type": "festival", "attire_tags": ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath-puja"], "is_festive": True},
    ("800008", "2026-10-04"): {"event_name": "Jitiya (Jivitputrika Vrat)", "event_type": "festival", "attire_tags": ["saree", "ethnic", "traditional", "red", "maroon"], "is_festive": True},
    ("800008", "2026-03-22"): {"event_name": "Bihar Diwas (Bihar Day)", "event_type": "festival", "attire_tags": ["saree", "salwar", "bhagalpuri-silk", "kurta", "dhoti", "nehru-jacket", "white", "cream", "patna"], "is_festive": True},
    ("800008", "2026-04-23"): {"event_name": "Veer Kunwar Singh Jayanti", "event_type": "festival", "attire_tags": ["kurta", "white", "cream"], "is_festive": True},
    ("800008", "2026-01-24"): {"event_name": "Karpoori Thakur Jayanti", "event_type": "festival", "attire_tags": ["shawl", "warm", "winter", "jacket", "white"], "is_festive": True},
    ("800008", "2026-10-21"): {"event_name": "Shri Krishna Singh Jayanti", "event_type": "festival", "attire_tags": ["saree", "salwar", "kurta", "white", "beige"], "is_festive": True},
    ("800008", "2026-03-26"): {"event_name": "Emperor Ashoka Ashtami", "event_type": "festival", "attire_tags": ["cotton", "saree", "suit", "white", "pastel"], "is_festive": True},
    ("800008", "2026-01-03"): {"event_name": "Prakash Parv (Patna Sahib)", "event_type": "festival", "attire_tags": ["traditional", "white", "blue", "saffron"], "is_festive": True},
    ("800008", "2026-02-02"): {"event_name": "Saraswati Puja (Vasant Panchami)", "event_type": "festival", "attire_tags": ["saree", "kurta", "yellow", "ethnic"], "is_festive": True},
    ("800008", "2026-08-10"): {"event_name": "Shravani Mela Pilgrim Cycle", "event_type": "festival", "attire_tags": ["saffron", "dhoti"], "is_festive": True},
    ("800008", "2026-12-09"): {"event_name": "Patna Pre-Wedding (Haldi Ceremony)", "event_type": "pre_wedding", "attire_tags": ["cotton", "yellow", "saffron", "ethnic"], "is_festive": True},
    ("800008", "2026-12-10"): {"event_name": "Patna Wedding Day (Pheras Ritual)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "traditional_embroidery", "ceremonial", "silk", "saree", "sherwani", "crimson", "gold", "maroon"], "is_festive": True},
    ("800008", "2026-12-11"): {"event_name": "Patna Post-Wedding (Vidaai Ceremony)", "event_type": "post_wedding", "attire_tags": ["festive", "magenta", "fuchsia", "gold", "ethnic"], "is_festive": True},
    
    # Kochi
    ("682001", "2026-08-27"): {"event_name": "Onam Festival (Thiruvonam)", "event_type": "festival", "attire_tags": ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"], "is_festive": True},
    ("682001", "2026-04-14"): {"event_name": "Vishu (New Year)", "event_type": "festival", "attire_tags": ["ethnic", "yellow", "gold", "cream"], "is_festive": True},
    ("682001", "2026-04-03"): {"event_name": "Good Friday Church Service", "event_type": "festival", "attire_tags": ["modest", "formal", "premium", "white"], "is_festive": False},
    ("682001", "2026-04-05"): {"event_name": "Easter Sunday Celebration", "event_type": "festival", "attire_tags": ["modest", "formal", "premium", "pastel"], "is_festive": True},
    ("682001", "2026-09-12"): {"event_name": "Synagogue Rosh Hashanah", "event_type": "festival", "attire_tags": ["subtle", "modest", "premium", "elegant"], "is_festive": True},
    ("682001", "2026-01-15"): {"event_name": "Makaravilakku Devotional", "event_type": "festival", "attire_tags": ["black", "saffron", "traditional", "mundu", "dhoti"], "is_festive": False},
    ("682001", "2026-01-25"): {"event_name": "Chandanakudam Festival (Mosque)", "event_type": "festival", "attire_tags": ["traditional", "Islamic", "modest", "ethnic", "embroidered"], "is_festive": True},
    ("682001", "2026-12-28"): {"event_name": "Indira Gandhi Boat Race", "event_type": "festival", "attire_tags": ["casual", "breathable", "cotton", "coastal"], "is_festive": True},
    ("682001", "2026-12-31"): {"event_name": "Cochin Carnival NYE", "event_type": "festival", "attire_tags": ["vibrant", "party", "bohemian", "modern"], "is_festive": True},
    ("682001", "2026-01-20"): {"event_name": "Kochi-Muziris Biennale Art Peak", "event_type": "festival", "attire_tags": ["artsy", "bohemian", "linen", "sustainable", "modern"], "is_festive": True},
    ("682001", "2026-12-26"): {"event_name": "Kochi Pre-Wedding (Nischayam)", "event_type": "pre_wedding", "attire_tags": ["semi-ethnic", "mint", "peach", "lavender", "pastel"], "is_festive": True},
    ("682001", "2026-12-27"): {"event_name": "Kochi Wedding Day (Thalikettu)", "event_type": "wedding_day", "attire_tags": ["kasavu_weave", "off-white", "cream", "gold"], "is_festive": True},
    ("682001", "2026-12-29"): {"event_name": "Kochi Post-Wedding (Reception)", "event_type": "post_wedding", "attire_tags": ["contemporary_fusion", "royal-blue", "wine", "black", "silver"], "is_festive": True},
    
    # Shillong
    ("793003", "2026-11-15"): {"event_name": "Shillong Cherry Blossom Fest", "event_type": "festival", "attire_tags": ["streetwear", "jacket", "coat", "scarf", "boots"], "is_festive": True},
    ("793003", "2026-12-25"): {"event_name": "Christmas Day Celebration", "event_type": "festival", "attire_tags": ["velvet", "woolen", "dress", "formal", "winter"], "is_festive": True},
    ("793003", "2026-04-15"): {"event_name": "Shad Suk Mynsiem Harvest Fest", "event_type": "festival", "attire_tags": ["jainsem", "jymphong", "traditional", "ethnic", "silk"], "is_festive": True},
    ("793003", "2026-10-25"): {"event_name": "Shillong Autumn Festival", "event_type": "festival", "attire_tags": ["indie", "fusion", "denim-fusion", "streetwear"], "is_festive": True},
    ("793003", "2026-11-10"): {"event_name": "Wangala Festival (100 Drums)", "event_type": "festival", "attire_tags": ["traditional", "tribal_heritage", "headgear", "accessories"], "is_festive": True},
    ("793003", "2026-07-14"): {"event_name": "Behdiengkhlam Festival", "event_type": "festival", "attire_tags": ["traditional"], "is_festive": True},
    ("793003", "2026-12-19"): {"event_name": "Shillong Pre-Wedding (Pynhiar Synjat)", "event_type": "pre_wedding", "attire_tags": ["western_formal", "silver", "white", "pastel", "fusion"], "is_festive": True},
    ("793003", "2026-12-20"): {"event_name": "Shillong Wedding Day (Traditional)", "event_type": "wedding_day", "attire_tags": ["handwoven_silk", "tribal_heritage", "jainsem", "jymphong", "earth-tones"], "is_festive": True},
    ("793003", "2026-12-21"): {"event_name": "Shillong Post-Wedding (Reception)", "event_type": "post_wedding", "attire_tags": ["western_formal", "navy", "burgundy", "black", "metallic"], "is_festive": True},

    # Universal Civic, Academic & Social Velocity Events (Regional Variations)
    # 1. Republic Day (Jan 26)
    ("800008", "2026-01-26"): {"event_name": "Republic Day Parade", "event_type": "festival", "attire_tags": ["white", "saffron", "green", "ethnic", "formal"], "is_festive": True},
    ("682001", "2026-01-26"): {"event_name": "Republic Day Parade", "event_type": "festival", "attire_tags": ["white", "fusion", "formal", "lightweight"], "is_festive": True},
    ("793003", "2026-01-26"): {"event_name": "Republic Day Parade", "event_type": "festival", "attire_tags": ["white", "saffron", "green", "winter", "jacket", "formal"], "is_festive": True},

    # 2. Holi (Mar 3)
    ("800008", "2026-03-03"): {"event_name": "Holi Festival of Colors", "event_type": "festival", "attire_tags": ["white", "cotton", "casual", "dailywear"], "is_festive": True},
    ("682001", "2026-03-03"): {"event_name": "Holi Festival of Colors", "event_type": "festival", "attire_tags": ["casual", "streetwear", "denim", "cotton"], "is_festive": True},
    ("793003", "2026-03-03"): {"event_name": "Holi Festival of Colors", "event_type": "festival", "attire_tags": ["hoodie", "winter", "warm", "streetwear"], "is_festive": True},

    # 3. Good Friday / Easter (Apr 5)
    ("800008", "2026-04-05"): {"event_name": "Easter Sunday Service", "event_type": "festival", "attire_tags": ["ethnic", "formal", "modest", "pastel"], "is_festive": True},
    ("793003", "2026-04-05"): {"event_name": "Easter Sunday Service", "event_type": "festival", "attire_tags": ["western_formal", "navy", "black", "grey", "suit", "gown"], "is_festive": True},

    # 4. Eid-ul-Fitr (Mar 20)
    ("800008", "2026-03-20"): {"event_name": "Eid-ul-Fitr Celebration", "event_type": "festival", "attire_tags": ["ethnic", "festive", "traditional_embroidery", "embroidered", "kurta", "sherwani"], "is_festive": True},
    ("682001", "2026-03-20"): {"event_name": "Eid-ul-Fitr Celebration", "event_type": "festival", "attire_tags": ["ethnic", "festive", "modest", "elegant"], "is_festive": True},
    ("793003", "2026-03-20"): {"event_name": "Eid-ul-Fitr Celebration", "event_type": "festival", "attire_tags": ["western_formal", "modest", "fusion"], "is_festive": True},

    # 5. Independence Day (Aug 15)
    ("800008", "2026-08-15"): {"event_name": "Independence Day Ceremony", "event_type": "festival", "attire_tags": ["saffron", "white", "green", "ethnic", "formal", "cotton"], "is_festive": True},
    ("682001", "2026-08-15"): {"event_name": "Independence Day Ceremony", "event_type": "festival", "attire_tags": ["saffron", "white", "green", "ethnic", "formal", "lightweight"], "is_festive": True},
    ("793003", "2026-08-15"): {"event_name": "Independence Day Ceremony", "event_type": "festival", "attire_tags": ["saffron", "white", "green", "formal", "jacket", "layered"], "is_festive": True},

    # 6. Durga Puja (Oct 18)
    ("800008", "2026-10-18"): {"event_name": "Durga Puja Peak Pandals", "event_type": "festival", "attire_tags": ["ethnic", "festive", "silk", "saree", "heavy_silk", "traditional"], "is_festive": True},
    ("682001", "2026-10-18"): {"event_name": "Durga Puja Celebrations", "event_type": "festival", "attire_tags": ["ethnic", "festive", "minimalist", "cotton"], "is_festive": True},
    ("793003", "2026-10-18"): {"event_name": "Durga Puja Autumn Fusion", "event_type": "festival", "attire_tags": ["streetwear", "fusion", "modern"], "is_festive": True},

    # 7. Diwali (Nov 8)
    ("800008", "2026-11-08"): {"event_name": "Diwali Lights Festival", "event_type": "festival", "attire_tags": ["ethnic", "festive", "traditional", "regal", "gold", "silk"], "is_festive": True},
    ("682001", "2026-11-08"): {"event_name": "Diwali Lights Festival", "event_type": "festival", "attire_tags": ["ethnic", "festive", "contemporary_fusion", "fusion", "earth-tones"], "is_festive": True},
    ("793003", "2026-11-08"): {"event_name": "Diwali Festival of Lights", "event_type": "festival", "attire_tags": ["winter", "warm", "jacket", "velvet", "festive"], "is_festive": True},

    # 8. Christmas Day (Dec 25)
    ("800008", "2026-12-25"): {"event_name": "Christmas Day Celebrations", "event_type": "festival", "attire_tags": ["winter", "party", "jacket", "velvet", "warm"], "is_festive": True},
    ("682001", "2026-12-25"): {"event_name": "Christmas Day Celebrations", "event_type": "festival", "attire_tags": ["vibrant", "party", "bohemian", "modern", "western"], "is_festive": True},

    # 9. College Farewells (Apr 10)
    ("800008", "2026-04-10"): {"event_name": "College Farewell Gala", "event_type": "festival", "attire_tags": ["formal", "saree", "suit", "ethnic"], "is_festive": True},
    ("682001", "2026-04-10"): {"event_name": "College Farewell Gala", "event_type": "festival", "attire_tags": ["pastel", "fusion", "cotton", "lightweight"], "is_festive": True},
    ("793003", "2026-04-10"): {"event_name": "College Farewell Gala", "event_type": "festival", "attire_tags": ["western_formal", "navy", "black", "grey", "blazer", "suit"], "is_festive": True},

    # 10. Graduation / Annual (May 15)
    ("800008", "2026-05-15"): {"event_name": "Annual Convocation Ceremony", "event_type": "festival", "attire_tags": ["formal", "ethnic", "fusion"], "is_festive": True},
    ("682001", "2026-05-15"): {"event_name": "Annual Convocation Ceremony", "event_type": "festival", "attire_tags": ["formal", "elegant", "premium"], "is_festive": True},
    ("793003", "2026-05-15"): {"event_name": "Annual Convocation Ceremony", "event_type": "festival", "attire_tags": ["western_formal", "suit", "gown", "blazer"], "is_festive": True},

    # 11. Annual School Day (Dec 5)
    ("800008", "2026-12-05"): {"event_name": "Annual School Day Celebration", "event_type": "festival", "attire_tags": ["formal", "smart_casual", "ethnic"], "is_festive": True},
    ("682001", "2026-12-05"): {"event_name": "Annual School Day Celebration", "event_type": "festival", "attire_tags": ["formal", "smart_casual", "ethnic"], "is_festive": True},
    ("793003", "2026-12-05"): {"event_name": "Annual School Day Celebration", "event_type": "festival", "attire_tags": ["formal", "smart_casual", "ethnic"], "is_festive": True},

    # 12. Back-to-College (Jul 5)
    ("800008", "2026-07-05"): {"event_name": "Back-to-College Opening", "event_type": "festival", "attire_tags": ["casual", "streetwear", "cotton", "breathable"], "is_festive": False},
    ("682001", "2026-07-05"): {"event_name": "Back-to-College Opening", "event_type": "festival", "attire_tags": ["casual", "streetwear", "linen", "breathable"], "is_festive": False},
    ("793003", "2026-07-05"): {"event_name": "Back-to-College Opening", "event_type": "festival", "attire_tags": ["casual", "streetwear", "jacket", "coat", "winter"], "is_festive": False},

    # 13. College Fests (Feb 15)
    ("800008", "2026-02-15"): {"event_name": "Annual College Fest", "event_type": "festival", "attire_tags": ["indie", "streetwear", "denim", "graphic"], "is_festive": True},
    ("682001", "2026-02-15"): {"event_name": "Annual College Fest", "event_type": "festival", "attire_tags": ["indie", "streetwear", "denim", "graphic"], "is_festive": True},
    ("793003", "2026-02-15"): {"event_name": "Annual College Fest", "event_type": "festival", "attire_tags": ["indie", "streetwear", "denim", "graphic"], "is_festive": True},

    # 14. Wedding Guest Day (Nov 25)
    ("800008", "2026-11-25"): {"event_name": "Wedding Guest Ceremony", "event_type": "festival", "attire_tags": ["ethnic", "festive", "silk", "velvet", "traditional"], "is_festive": True},
    ("682001", "2026-11-25"): {"event_name": "Wedding Guest Ceremony", "event_type": "festival", "attire_tags": ["ethnic", "festive", "silk", "velvet", "traditional"], "is_festive": True},
    ("793003", "2026-11-25"): {"event_name": "Wedding Guest Ceremony", "event_type": "festival", "attire_tags": ["ethnic", "festive", "silk", "velvet", "traditional"], "is_festive": True},

    # 15. Office Ethnic Day (Sep 4)
    ("800008", "2026-09-04"): {"event_name": "Office Ethnic Day", "event_type": "festival", "attire_tags": ["ethnic", "subtle", "pastel", "minimalist", "kurta", "saree"], "is_festive": True},
    ("682001", "2026-09-04"): {"event_name": "Office Ethnic Day", "event_type": "festival", "attire_tags": ["ethnic", "subtle", "pastel", "minimalist", "kurta", "saree"], "is_festive": True},
    ("793003", "2026-09-04"): {"event_name": "Office Ethnic Day", "event_type": "festival", "attire_tags": ["ethnic", "subtle", "pastel", "minimalist", "kurta", "saree"], "is_festive": True},

    # 16. College Admissions (Jul 15)
    ("800008", "2026-07-15"): {"event_name": "College Admissions Season", "event_type": "festival", "attire_tags": ["smart_casual", "breathable_cotton", "modest_fusion", "summer_wear"], "is_festive": False},
    ("682001", "2026-07-15"): {"event_name": "College Admissions Season", "event_type": "festival", "attire_tags": ["monsoon_ready", "contemporary_casual", "dark_tones", "minimalist"], "is_festive": False},
    ("793003", "2026-07-15"): {"event_name": "College Admissions Season", "event_type": "festival", "attire_tags": ["streetwear", "light_layers", "western_casual", "trendy_youth"], "is_festive": False}
}

# Local Velocity Cache (fallback when Supabase is offline)
# Mirrors the seed data in schema.sql
LOCAL_VELOCITY_CACHE = {
    # Patna
    (1,  "800008"): {"velocity_score": 0.92, "units_last_hour": 47},
    (2,  "800008"): {"velocity_score": 0.88, "units_last_hour": 38},
    (7,  "800008"): {"velocity_score": 0.75, "units_last_hour": 22},
    (9,  "800008"): {"velocity_score": 0.65, "units_last_hour": 18},
    (13, "800008"): {"velocity_score": 0.70, "units_last_hour": 20},
    (15, "800008"): {"velocity_score": 0.80, "units_last_hour": 30},
    (11, "800008"): {"velocity_score": 0.55, "units_last_hour": 12},
    (48, "800008"): {"velocity_score": 0.60, "units_last_hour": 15},
    (6,  "800008"): {"velocity_score": 0.72, "units_last_hour": 24},
    # Kochi
    (16, "682001"): {"velocity_score": 0.95, "units_last_hour": 52},
    (17, "682001"): {"velocity_score": 0.85, "units_last_hour": 35},
    (25, "682001"): {"velocity_score": 0.78, "units_last_hour": 28},
    (28, "682001"): {"velocity_score": 0.70, "units_last_hour": 20},
    (20, "682001"): {"velocity_score": 0.62, "units_last_hour": 16},
    (26, "682001"): {"velocity_score": 0.55, "units_last_hour": 11},
    (23, "682001"): {"velocity_score": 0.50, "units_last_hour":  9},
    (24, "682001"): {"velocity_score": 0.58, "units_last_hour": 14},
    (30, "682001"): {"velocity_score": 0.45, "units_last_hour":  7},
    # Shillong
    (31, "793003"): {"velocity_score": 0.90, "units_last_hour": 42},
    (32, "793003"): {"velocity_score": 0.82, "units_last_hour": 32},
    (33, "793003"): {"velocity_score": 0.78, "units_last_hour": 26},
    (36, "793003"): {"velocity_score": 0.72, "units_last_hour": 22},
    (37, "793003"): {"velocity_score": 0.68, "units_last_hour": 19},
    (41, "793003"): {"velocity_score": 0.65, "units_last_hour": 17},
    (44, "793003"): {"velocity_score": 0.60, "units_last_hour": 14},
    (40, "793003"): {"velocity_score": 0.55, "units_last_hour": 10},
    (39, "793003"): {"velocity_score": 0.75, "units_last_hour": 25},
}

def get_velocity_map(zip_code: str, supabase_url: str = None, supabase_key: str = None) -> dict:
    """Returns {product_id -> {velocity_score, units_last_hour}} for a given zip code."""
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            sb = create_client(supabase_url, supabase_key)
            res = sb.table("checkout_velocity") \
                .select("product_id, velocity_score, units_last_hour") \
                .eq("zip_code", zip_code) \
                .execute()
            if res.data:
                logger.info(f"Fetched {len(res.data)} velocity rows from Supabase for {zip_code}")
                return {row["product_id"]: row for row in res.data}
        except Exception as e:
            logger.warning(f"Velocity fetch from Supabase failed: {e}. Using local cache.")
    # Fallback to local cache
    return {
        pid: data
        for (pid, zc), data in LOCAL_VELOCITY_CACHE.items()
        if zc == zip_code
    }

# Local Outfit Completer Cache (fallback when Supabase is offline)
# Maps primary_item_id -> {suggested_accessory_id, suggested_footwear_id, occasion_tag}
# IDs verified against actual catalog (IDs 1-159):
#   ID=124: Heavy kundan necklace set
#   ID=127: Traditional silver anklets
#   ID=135: Minimalist gold earring set
#   ID=149: Modern ankle boots for women
#   ID=38:  Wangala Tribal Beaded Vest
LOCAL_OUTFIT_COMPLETER = {
    (1, "wedding_day"): {"suggested_accessory_id": 124, "suggested_footwear_id": 149}, # Crimson Banarasi Silk Saree -> Kundan Necklace + Boots
    (2, "wedding_day"): {"suggested_accessory_id": 124, "suggested_footwear_id": 149}, # Sherwani -> Kundan Necklace + Boots
    (9, "festival"):    {"suggested_accessory_id": 127, "suggested_footwear_id": 149}, # Yellow Saree -> Anklets + Boots
    (7, "festival"):    {"suggested_accessory_id": 127, "suggested_footwear_id": None}, # Chhath Saree -> Anklets
    (16, "festival"):   {"suggested_accessory_id": 127, "suggested_footwear_id": None}, # Onam Kasavu Saree -> Anklets
    (97, "wedding_day"):{"suggested_accessory_id": 124, "suggested_footwear_id": 149}, # Kasavu Saree -> Kundan + Boots
    (110, "festival"):  {"suggested_accessory_id": 38,  "suggested_footwear_id": 149}, # Cherry Blossom -> Beaded Vest + Boots
    (112, "festival"):  {"suggested_accessory_id": 135, "suggested_footwear_id": 149}, # Christmas Velvet -> Earrings + Boots
    # Wedding day fallbacks for other regional sarees
    (6, "wedding_day"):  {"suggested_accessory_id": 124, "suggested_footwear_id": 149}, # Bhagalpuri Silk
    (5, "festival"):     {"suggested_accessory_id": 156, "suggested_footwear_id": 149}, # Fuchsia Mooh Dikhayi Saree -> Engagement ring
    (17, "festival"):    {"suggested_accessory_id": 127, "suggested_footwear_id": None}, # Onam Kasavu Dress
    (120, "festival"):   {"suggested_accessory_id": 135, "suggested_footwear_id": 149}, # Party wear
    (143, "festival"):   {"suggested_accessory_id": 139, "suggested_footwear_id": 149}, # Silver neckpiece -> Sunglasses + Boots
}

# Vibe vector calculations
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

def get_macro_trends(zip_code: str, date_str: str):
    """Retrieves macro trends based on season and region.
    
    Returns region-contextual trends that blend seasonal signals with the
    cultural attire norms of each geography to avoid overriding festive signals.
    """
    try:
        month = int(date_str.split("-")[1])
    except Exception:
        month = 8

    # Map ZIP codes to canonical region names
    region_map = {
        "800001": "patna", "800008": "patna",
        "560034": "kochi", "682001": "kochi",
        "110049": "shillong", "793003": "shillong"
    }
    region = region_map.get(zip_code, "patna")

    if region == "patna":
        # Patna: Heavy festive Oct-Dec, cold Jan-Feb, hot summers
        if month in [10, 11, 12]:
            # Festive + wedding season + mild cool blend - don't push pure winter trends
            return ["ethnic", "festive", "silk", "traditional", "saree", "shawl", "warm"]
        elif month in [1, 2]:
            return ["winter", "shawl", "warm", "jacket", "traditional", "ethnic"]
        elif month in [3, 4]:
            return ["ethnic", "traditional", "bright", "pastel", "casual"]
        elif month in [5, 6]:
            return ["cotton", "breathable", "casual", "summer", "linen"]
        else:  # 7, 8, 9
            return ["cotton", "breathable", "casual", "dailywear", "traditional"]

    elif region == "kochi":
        # Kochi: Tropical, Onam peak Aug-Sep, Christmas/NYE Dec-Jan
        if month in [8, 9]:
            return ["kasavu_weave", "white", "ethnic", "saree", "mundu", "traditional", "cotton"]
        elif month in [12, 1]:
            return ["party", "bohemian", "vibrant", "modern", "casual", "coastal"]
        elif month in [6, 7, 10, 11]:
            return ["cotton", "breathable", "casual", "modest", "linen"]
        else:
            return ["cotton", "breathable", "linen", "casual", "summer", "bohemian"]

    else:  # shillong / delhi
        # Shillong: Cool/Cold most of year, streetwear/western
        if month in [11, 12, 1, 2]:
            return ["winter", "jacket", "velvet", "woolen", "streetwear", "western_formal"]
        elif month in [3, 4]:
            return ["streetwear", "ethnic", "fusion", "western_formal", "casual"]
        else:
            return ["streetwear", "denim", "casual", "fusion", "modern", "indie"]


def compute_cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b:
        return 0.0
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))

# Weather Matrix throughout the year for the three zip codes
WEATHER_MATRIX = {
    "800008": { # Patna
        1: {"desc": "Cool & Dry", "temp": "10°C–22°C", "cold_wave": True, "hot_wave": False, "rainy": False},
        2: {"desc": "Warm & Dry", "temp": "12°C–26°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        3: {"desc": "Getting Hot", "temp": "17°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        4: {"desc": "Hot & Dry", "temp": "21°C–38°C", "cold_wave": False, "hot_wave": True, "rainy": False},
        5: {"desc": "Very Hot", "temp": "24°C–39°C", "cold_wave": False, "hot_wave": True, "rainy": False},
        6: {"desc": "Hot & Humid", "temp": "25°C–35°C", "cold_wave": False, "hot_wave": True, "rainy": False},
        7: {"desc": "Hot & Monsoon", "temp": "26°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        8: {"desc": "Humid & Wet", "temp": "25°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        9: {"desc": "Humid", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        10: {"desc": "Pleasant", "temp": "20°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        11: {"desc": "Cool & Dry", "temp": "15°C–27°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        12: {"desc": "Cold & Dry", "temp": "11°C–23°C", "cold_wave": True, "hot_wave": False, "rainy": False}
    },
    "682001": { # Fort Kochi
        1: {"desc": "Pleasant & Dry", "temp": "23°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        2: {"desc": "Pleasant & Dry", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        3: {"desc": "Warm & Humid", "temp": "25°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        4: {"desc": "Hot & Humid", "temp": "27°C–33°C", "cold_wave": False, "hot_wave": True, "rainy": False},
        5: {"desc": "Hot & Wet", "temp": "27°C–31°C", "cold_wave": False, "hot_wave": True, "rainy": True},
        6: {"desc": "Wet/Monsoon", "temp": "26°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        7: {"desc": "Peak Monsoon", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        8: {"desc": "Monsoon", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        9: {"desc": "Monsoon Subsiding", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        10: {"desc": "Warm & Humid", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        11: {"desc": "Warm & Dry", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        12: {"desc": "Pleasant & Dry", "temp": "24°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False}
    },
    "793003": { # Shillong
        1: {"desc": "Cold & Dry", "temp": "8°C–17°C", "cold_wave": True, "hot_wave": False, "rainy": False},
        2: {"desc": "Cool & Dry", "temp": "10°C–19°C", "cold_wave": True, "hot_wave": False, "rainy": False},
        3: {"desc": "Pleasant", "temp": "13°C–22°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        4: {"desc": "Mild & Rainy", "temp": "16°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        5: {"desc": "Mild & Rainy", "temp": "17°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        6: {"desc": "Cool & Rainy", "temp": "19°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        7: {"desc": "Cool & Wet", "temp": "20°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        8: {"desc": "Cool & Wet", "temp": "19°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        9: {"desc": "Cool & Wet", "temp": "19°C–23°C", "cold_wave": False, "hot_wave": False, "rainy": True},
        10: {"desc": "Pleasant", "temp": "16°C–22°C", "cold_wave": False, "hot_wave": False, "rainy": False},
        11: {"desc": "Cool & Dry", "temp": "12°C–20°C", "cold_wave": True, "hot_wave": False, "rainy": False},
        12: {"desc": "Cold & Dry", "temp": "9°C–18°C", "cold_wave": True, "hot_wave": False, "rainy": False}
    }
}

@app.get("/api/system-state")
def get_system_state():
    supabase_configured = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    return {
        "status": "online",
        "database_connected": supabase_configured,
        "database_engine": "Supabase pgvector" if supabase_configured else "Local In-Memory Similarity Simulation"
    }

def map_zip_code(zip_code: str) -> str:
    # Map new ZIP codes to existing calendar/weather ZIP codes if needed
    mapping = {
        "800001": "800008", # Patna
        "560034": "682001", # Koramangala -> Kochi (for calendar/weather mock fallback)
        "110049": "793003"  # South Ext -> Shillong (for calendar/weather mock fallback)
    }
    return mapping.get(zip_code, zip_code)

def get_boutique_trends(zip_code: str) -> list:
    """Fetches boutique trends from local JSON file and matches them to catalog products."""
    local_trends_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "real_trends_seed.json"))
    local_catalog_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_catalog.json"))
    
    # Handle zip mappings for backward compatibility
    zip_mapping = {
        "800008": "800001",
        "682001": "560034",
        "793003": "110049"
    }
    target_zip = zip_mapping.get(zip_code, zip_code)
    
    trends = []
    if os.path.exists(local_trends_file):
        try:
            with open(local_trends_file, "r") as f:
                raw_trends = json.load(f)
                trends = [t for t in raw_trends if t["zip_code"] == target_zip]
        except Exception as e:
            logger.error(f"Failed to read local boutique trends: {e}")
            
    catalog = []
    if os.path.exists(local_catalog_file):
        try:
            with open(local_catalog_file, "r") as f:
                catalog = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local catalog: {e}")
            
    enriched_boutiques = []
    for idx, t in enumerate(trends):
        store_name = t["store_name"]
        trend = t["extracted_visual_trend"]
        locality = t["locality"]
        
        # Deterministic rating (e.g. 4.3 to 4.9) and address based on store name length
        rating = round(4.2 + (len(store_name) % 8) * 0.1, 1)
        address = f"Shop {10 + (idx % 5)}, Commercial Complex, {locality}"
        
        # Google Maps URL
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(f"{store_name} {locality}")
        maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
        
        # Find best matching product
        matched_product = None
        if catalog:
            trend_words = set(trend.lower().replace("-", " ").split())
            best_match = None
            best_score = -1
            for p in catalog:
                product_tags = set(tag.lower() for tag in p.get("tags", []))
                overlap = len(trend_words.intersection(product_tags))
                score = overlap * 1.0
                
                # Boost specific mappings
                if trend == "banarasi-silk" and ("silk" in product_tags or "banarasi" in product_tags):
                    score += 3
                elif trend == "tussar-saree" and ("saree" in product_tags or "silk" in product_tags):
                    score += 3
                elif trend == "heavy-anarkali" and ("anarkali" in product_tags or "ethnic" in product_tags):
                    score += 3
                elif trend == "festive-kurta-set" and ("kurta" in product_tags or "festive" in product_tags):
                    score += 3
                elif trend == "y2k-crop" and ("streetwear" in product_tags or "cropped" in product_tags or "tee" in product_tags):
                    score += 3
                elif trend == "baggy-jeans" and ("jeans" in product_tags or "denim" in product_tags):
                    score += 3
                elif trend == "oversized-tees" and ("tee" in product_tags or "hoodie" in product_tags):
                    score += 3
                elif trend == "cargo-pants" and ("cargo" in product_tags or "pants" in product_tags):
                    score += 3
                elif trend == "varsity-jackets" and ("jacket" in product_tags or "streetwear" in product_tags):
                    score += 3
                elif trend == "indo-western-gown" and ("gown" in product_tags or "dress" in product_tags):
                    score += 3
                elif trend == "pastel-lehenga" and ("lehenga" in product_tags or "festive" in product_tags):
                    score += 3
                elif trend == "chikankari-kurti" and ("kurta" in product_tags or "cotton" in product_tags):
                    score += 3
                elif trend == "designer-dupatta" and ("dupatta" in product_tags or "silk" in product_tags):
                    score += 3
                    
                if score > best_score:
                    best_score = score
                    best_match = p
            matched_product = best_match
            
        enriched_boutiques.append({
            "store_id": t["store_id"],
            "store_name": store_name,
            "locality": locality,
            "address": address,
            "rating": rating,
            "maps_url": maps_url,
            "social_signal_source": t["social_signal_source"],
            "simulated_engagement": t["simulated_engagement"],
            "extracted_visual_trend": trend,
            "style_vibe_cluster": t["style_vibe_cluster"],
            "matched_product": matched_product
        })
        
    return enriched_boutiques

@app.get("/api/trends/boutiques")
def get_boutiques_endpoint(zip_code: str):
    """
    Returns the boutique trend entries for the given ZIP code.
    """
    try:
        trends = get_boutique_trends(zip_code)
        return {"zip_code": zip_code, "boutiques": trends}
    except Exception as e:
        logger.error(f"Error fetching boutique trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
def get_products(
    zip_code: str = Query("800008"), 
    date: str = Query("2026-08-15"), 
    vibe: str = Query("casual")
):
    """
    Ranks products matching regional filters (zip_code) using the 6-Layer Hyper-Local Personalization Engine.
    """
    # Map ZIP codes for fallback calendar/weather data
    mapped_zip = map_zip_code(zip_code)
    
    # 1. Determine active calendar event
    active_event = None
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if supabase_url and supabase_key:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            cal_res = supabase.table("calendar")\
                .select("event_name, event_type, attire_tags, is_festive")\
                .eq("zip_code", mapped_zip)\
                .eq("date", date)\
                .execute()
                
            if cal_res.data and len(cal_res.data) > 0:
                active_event = cal_res.data[0]
                logger.info(f"Database calendar match found for {mapped_zip}: {active_event['event_name']}")
        except Exception as e:
            logger.error(f"Supabase calendar query error: {e}")
            
    # Fallback to local dict if DB not queried or returned nothing
    if not active_event:
        active_event = FALLBACK_CALENDAR.get((mapped_zip, date))
        if active_event:
            logger.info(f"Local fallback calendar match found for {mapped_zip}: {active_event['event_name']}")
            
    # 2. Set up variables based on calendar event
    event_name = active_event.get("event_name", "Baseline Routine Day") if active_event else "Baseline Routine Day"
    event_type = active_event.get("event_type", "festival") if active_event else "festival"
    target_event_tags = active_event.get("attire_tags", []) if active_event else []
    is_festive_season = active_event.get("is_festive", False) if active_event else False
    is_wedding_day = (event_type == "wedding_day")
    
    # Calculate climate variables based on date & location
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        month = dt.month
    except Exception:
        month = 8
        
    is_cold_wave = False
    is_hot_wave = False
    is_rainy = False
    
    if mapped_zip in WEATHER_MATRIX and month in WEATHER_MATRIX[mapped_zip]:
        weather_entry = WEATHER_MATRIX[mapped_zip][month]
        is_cold_wave = weather_entry["cold_wave"]
        is_hot_wave = weather_entry["hot_wave"]
        is_rainy = weather_entry["rainy"]
    
    # Determine creator/macro trends
    creator_trends = get_macro_trends(zip_code, date)
    user_vector = get_vibe_vector(vibe)
    
    # Fetch velocity mapping (using the requested zip_code)
    velocity_map = get_velocity_map(zip_code, supabase_url, supabase_key)
    
    # Fetch boutique trends
    boutique_trends = get_boutique_trends(zip_code)
    
    # Calculate boutique trend weights based on engagement
    boutique_trend_weights = {}
    total_engagement = 0
    for b in boutique_trends:
        trend = b["extracted_visual_trend"]
        engagement = b["simulated_engagement"]
        boutique_trend_weights[trend] = boutique_trend_weights.get(trend, 0) + engagement
        total_engagement += engagement
        
    if total_engagement > 0:
        for t in boutique_trend_weights:
            boutique_trend_weights[t] /= total_engagement
            
    # Fetch products
    raw_products = []
    if supabase_url and supabase_key:
        try:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            prod_res = supabase.table("products").select("*").execute()
            if prod_res.data:
                raw_products = prod_res.data
        except Exception as e:
            logger.error(f"Failed to fetch products from Supabase: {e}. Falling back to local file.")
            
    if not raw_products:
        if not os.path.exists(LOCAL_CATALOG_FILE):
            raise HTTPException(
                status_code=500, 
                detail="Local catalog file not found. Run embed_catalog.py first."
            )
        try:
            with open(LOCAL_CATALOG_FILE, "r") as f:
                raw_products = json.load(f)
        except Exception as e:
            logger.error(f"In-memory catalog read error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    try:
        ranked_products = []
        for p in raw_products:
            # Geographic filter
            p_zips = p.get("zip_codes", [])
            # Allow matching either original or mapped zip codes
            if p_zips and zip_code not in p_zips and mapped_zip not in p_zips:
                continue # Skip items mapped strictly to other zip codes (e.g. Shillong micro-creators)
                
            p_tags = p.get("tags", [])
            
            # --- LAYER 1: Personal Vibe Match (35%) ---
            p_embed = p.get("embedding")
            # Handle potential string format from PostgreSQL vector column
            if isinstance(p_embed, str):
                try:
                    p_embed = json.loads(p_embed)
                except Exception:
                    pass
            sim = compute_cosine_similarity(user_vector, p_embed)
            personal_vibe_raw = max(0.0, min(1.0, sim))
            personal_vibe_score = personal_vibe_raw * 0.35
            
            # --- LAYER 2: Creator Trend Signal (20%) ---
            overlap_creator = [t for t in p_tags if t in creator_trends]
            creator_raw = min(1.0, len(overlap_creator) / 2.0) if creator_trends else 0.0
            creator_trend_score = creator_raw * 0.20
            
            # --- LAYER 3: Local Boutique Vibe (15%) ---
            boutique_raw = sum(boutique_trend_weights.get(t, 0) for t in p_tags if t in boutique_trend_weights)
            boutique_raw = min(1.0, boutique_raw)
            local_boutique_score = boutique_raw * 0.15
            
            # --- LAYER 4: Festivity / Calendar (15%) ---
            overlap_event = [t for t in p_tags if t in target_event_tags]
            festivity_raw = min(1.0, len(overlap_event) / 2.0) if target_event_tags else 0.0
            festivity_score = festivity_raw * 0.15
            
            # --- LAYER 5: Weather Conditions (10%) ---
            weather_raw = 0.0
            if is_cold_wave and "winter" in p_tags:
                weather_raw = 1.0
            elif is_hot_wave and ("summer" in p_tags or "breathable" in p_tags):
                weather_raw = 1.0
            elif is_rainy and ("cotton" in p_tags or "breathable" in p_tags):
                weather_raw = 1.0
            weather_score = weather_raw * 0.10
            
            # --- LAYER 6: Checkout Velocity (5%) ---
            velocity_entry = velocity_map.get(p["id"], velocity_map.get(str(p["id"]), {}))
            v_score = velocity_entry.get("velocity_score", 0.0)
            units = velocity_entry.get("units_last_hour", 0)
            velocity_score = v_score * 0.05
            
            # Compute Unified Score
            final_score = (
                personal_vibe_score + 
                creator_trend_score + 
                local_boutique_score + 
                festivity_score + 
                weather_score + 
                velocity_score
            )
            
            # Keep original boost variables for backward compatibility/ui display
            cold_boost = 0.15 if (is_cold_wave and "winter" in p_tags) else 0.0
            hot_boost = 0.15 if (is_hot_wave and ("summer" in p_tags or "breathable" in p_tags)) else 0.0
            rainy_boost = 0.15 if (is_rainy and ("cotton" in p_tags or "breathable" in p_tags)) else 0.0
            festive_boost = 0.15 if (is_festive_season and "festive" in p_tags) else 0.0
            wedding_boost = 0.3 if (is_wedding_day and "ceremonial" in p_tags) else 0.0
            event_boost = 0.15 if (len(target_event_tags) > 0 and any(t in p_tags for t in target_event_tags)) else 0.0
            boost_score = cold_boost + hot_boost + rainy_boost + festive_boost + wedding_boost + event_boost
            
            # --- APPLY STRICT HACKATHON RULES ---
            # Patna Pheras: Banarasi Silks must dominate, casual lightweight must fail
            if zip_code in ["800008", "800001"] and is_wedding_day:
                if "heavy_silk" in p_tags:
                    final_score += 0.50
                elif "summer" in p_tags or "casual" in p_tags:
                    final_score -= 0.50
                    
            # Kochi Thalikettu: Kasavu saree is non-negotiable
            if zip_code in ["682001", "560034"] and is_wedding_day:
                if "kasavu_weave" in p_tags:
                    final_score += 0.50
                    
            # Shillong Traditional: Jainsem & Jymphong handwoven pieces boost
            if zip_code in ["793003", "110049"] and is_wedding_day:
                if "handwoven_silk" in p_tags or "tribal_heritage" in p_tags:
                    final_score += 0.50
            
            is_trending = v_score >= 0.75
            velocity_boost = round(v_score * 0.20, 4) if v_score > 0 else 0.0
            
            ranked_products.append({
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "image_url": p["image_url"],
                "product_url": p.get("product_url", None),
                "tags": p_tags,
                "zip_codes": p_zips,
                "vector_score": personal_vibe_raw,
                "tag_score": creator_raw,
                "boost_score": boost_score,
                "velocity_score": v_score,
                "velocity_boost": velocity_boost,
                "units_last_hour": units,
                "is_trending": is_trending,
                "final_score": round(final_score, 4),
                "overlap_tags": list(set(p_tags) & (set(creator_trends) | set(target_event_tags))),
                
                # 6-Layer breakdown scores for visualization
                "scoring_breakdown": {
                    "layer1_personal_vibe": round(personal_vibe_score, 4),
                    "layer2_creator_trend": round(creator_trend_score, 4),
                    "layer3_local_boutique": round(local_boutique_score, 4),
                    "layer4_festivity": round(festivity_score, 4),
                    "layer5_weather": round(weather_score, 4),
                    "layer6_velocity": round(velocity_score, 4),
                    "raw_values": {
                        "personal_vibe_similarity": round(personal_vibe_raw, 4),
                        "creator_trend_match": round(creator_raw, 4),
                        "local_boutique_match": round(boutique_raw, 4),
                        "festivity_match": round(festivity_raw, 4),
                        "weather_match": round(weather_raw, 4),
                        "checkout_velocity_score": round(v_score, 4)
                    }
                }
            })
            
        ranked_products.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked_products
        
    except Exception as e:
        logger.error(f"Unified 6-layer calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from app.youtube_scraper import get_youtube_trend_match

@app.get("/api/trends/youtube")
def get_youtube_trends(zip_code: str):
    """
    Simulates scraping YouTube, extracting vision data, and matching it to our catalog.
    """
    try:
        result = get_youtube_trend_match(zip_code)
        return result
    except Exception as e:
        logger.error(f"YouTube trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/look-completer")
def get_look_completer(product_id: int, occasion_tag: str):
    """
    Retrieves recommended accessories and footwear matching the primary product and occasion.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    mapping = None
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            sb = create_client(supabase_url, supabase_key)
            res = sb.table("outfit_completer") \
                .select("suggested_accessory_id, suggested_footwear_id") \
                .eq("primary_item_id", product_id) \
                .eq("occasion_tag", occasion_tag) \
                .execute()
            if res.data and len(res.data) > 0:
                mapping = res.data[0]
                logger.info(f"Database Look Completer found: {mapping}")
        except Exception as e:
            logger.error(f"Supabase Look Completer query failed: {e}")

    if not mapping:
        mapping = LOCAL_OUTFIT_COMPLETER.get((product_id, occasion_tag))
        if mapping:
            logger.info(f"Local Fallback Look Completer found: {mapping}")

    if not mapping:
        return {"accessory": None, "footwear": None}

    # Fetch product metadata from local catalog file
    accessory_item = None
    footwear_item = None
    try:
        with open(LOCAL_CATALOG_FILE, 'r') as f:
            catalog = json.load(f)
            catalog_dict = {p["id"]: p for p in catalog}
            
            acc_id = mapping.get("suggested_accessory_id")
            foot_id = mapping.get("suggested_footwear_id")
            
            if acc_id and acc_id in catalog_dict:
                accessory_item = {
                    "id": acc_id,
                    "name": catalog_dict[acc_id]["name"],
                    "image_url": catalog_dict[acc_id]["image_url"],
                    "product_url": catalog_dict[acc_id].get("product_url")
                }
            if foot_id and foot_id in catalog_dict:
                footwear_item = {
                    "id": foot_id,
                    "name": catalog_dict[foot_id]["name"],
                    "image_url": catalog_dict[foot_id]["image_url"],
                    "product_url": catalog_dict[foot_id].get("product_url")
                }
    except Exception as e:
        logger.error(f"Failed to fetch accessory/footwear details from local catalog: {e}")

    return {
        "accessory": accessory_item,
        "footwear": footwear_item
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
