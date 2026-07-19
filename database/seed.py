import os
import json
import logging
import numpy as np
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_db")

# Load env variables from backend/.env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "local_catalog.json"))
BOUTIQUE_TRENDS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "real_trends_seed.json"))

def get_vibe_vector(vibe_name: str):
    """Calculates a deterministic 512-dimensional vibe vector."""
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

def get_vibe_vector_from_tags(tags: list):
    """Calculates a deterministic 512-dimensional vector based on list of tags."""
    vec = np.zeros(512)
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in ["ethnic", "festive", "saree", "lehenga", "traditional", "jainsem", "jymphong", "mundu", "sherwani", "ceremonial", "heavy_silk", "traditional_embroidery"]:
            vec[0:100] += 1.0
        if tag_lower in ["casual", "summer", "linen", "cotton", "breathable", "dailywear"]:
            vec[100:200] += 1.0
        if tag_lower in ["winter", "warm", "heavy-weight", "velvet", "shawl", "jacket", "cardigan", "woolen"]:
            vec[200:300] += 1.0
        if tag_lower in ["streetwear", "hoodie", "cargo", "modern", "denim", "fusion", "party", "trendy"]:
            vec[300:400] += 1.0
            
    vec[400:512] = 0.2
    
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
        
    return vec.tolist()

# Calendar Presets
CALENDAR_PRESETS = [
    # Patna
    {"zip_code": "800008", "date": "2026-11-15", "event_name": "Chhath Puja (Sandhya Arghya)", "event_type": "festival", "attire_tags": ["saree", "cotton", "traditional", "dhoti", "saffron", "yellow", "white", "patna", "chhath_puja"], "is_festive": True},
    {"zip_code": "800008", "date": "2026-02-02", "event_name": "Saraswati Puja (Vasant Panchami)", "event_type": "festival", "attire_tags": ["saree", "kurta", "yellow", "ethnic"], "is_festive": True},
    {"zip_code": "800008", "date": "2026-03-22", "event_name": "Bihar Diwas (Bihar Day)", "event_type": "festival", "attire_tags": ["saree", "salwar", "bhagalpuri_silk", "kurta", "dhoti", "nehru_jacket", "white", "cream", "patna"], "is_festive": True},
    {"zip_code": "800008", "date": "2026-12-10", "event_name": "Patna Wedding Day (Pheras)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "traditional_embroidery", "ceremonial", "silk", "saree", "sherwani", "crimson", "gold", "maroon"], "is_festive": True},
    # Kochi
    {"zip_code": "682001", "date": "2026-01-20", "event_name": "Kochi-Muziris Biennale Peak", "event_type": "festival", "attire_tags": ["artsy", "bohemian", "linen", "sustainable", "modern"], "is_festive": True},
    {"zip_code": "682001", "date": "2026-04-14", "event_name": "Vishu Festival (Malayali New Year)", "event_type": "festival", "attire_tags": ["ethnic", "yellow", "gold", "cream", "kasavu_weave"], "is_festive": True},
    {"zip_code": "682001", "date": "2026-08-27", "event_name": "Onam Festival (Thiruvonam)", "event_type": "festival", "attire_tags": ["saree", "mundu", "kasavu_weave", "white", "cream", "gold"], "is_festive": True},
    {"zip_code": "682001", "date": "2026-12-27", "event_name": "Kochi Wedding Day (Thalikettu)", "event_type": "wedding_day", "attire_tags": ["kasavu_weave", "off-white", "cream", "gold"], "is_festive": True},
    # Odisha
    {"zip_code": "752001", "date": "2026-01-14", "event_name": "Makar Sankranti (Makar Mela)", "event_type": "festival", "attire_tags": ["traditional", "tussar_silk", "yellow", "red", "odisha"], "is_festive": True},
    {"zip_code": "752001", "date": "2026-06-14", "event_name": "Pahili Raja (Raja Parba)", "event_type": "festival", "attire_tags": ["traditional", "cotton", "pastel", "lightweight", "sambalpuri"], "is_festive": True},
    {"zip_code": "752001", "date": "2026-06-15", "event_name": "Raja Sankranti Festival", "event_type": "festival", "attire_tags": ["traditional", "cotton", "pastel", "sambalpuri", "ethnic"], "is_festive": True},
    {"zip_code": "752001", "date": "2026-07-16", "event_name": "Puri Rath Yatra Chariot Festival", "event_type": "festival", "attire_tags": ["sambalpuri", "cotton", "traditional", "yellow", "saffron", "saree", "kurta"], "is_festive": True},
    {"zip_code": "752001", "date": "2026-12-20", "event_name": "Odisha Winter Wedding (Pheras)", "event_type": "wedding_day", "attire_tags": ["heavy_silk", "tussar_silk", "ceremonial", "sherwani", "crimson", "gold"], "is_festive": True},
]

# Checkout Velocity Presets
VELOCITY_PRESETS = [
    # Patna (800008)
    {"product_id": 1, "zip_code": "800008", "velocity_score": 0.92, "units_last_hour": 47},
    {"product_id": 2, "zip_code": "800008", "velocity_score": 0.88, "units_last_hour": 38},
    {"product_id": 7, "zip_code": "800008", "velocity_score": 0.75, "units_last_hour": 22},
    {"product_id": 9, "zip_code": "800008", "velocity_score": 0.65, "units_last_hour": 18},
    {"product_id": 13, "zip_code": "800008", "velocity_score": 0.70, "units_last_hour": 20},
    {"product_id": 15, "zip_code": "800008", "velocity_score": 0.80, "units_last_hour": 30},
    {"product_id": 11, "zip_code": "800008", "velocity_score": 0.55, "units_last_hour": 12},
    {"product_id": 48, "zip_code": "800008", "velocity_score": 0.60, "units_last_hour": 15},
    {"product_id": 6, "zip_code": "800008", "velocity_score": 0.72, "units_last_hour": 24},
    # Kochi (682001)
    {"product_id": 16, "zip_code": "682001", "velocity_score": 0.95, "units_last_hour": 52},
    {"product_id": 17, "zip_code": "682001", "velocity_score": 0.85, "units_last_hour": 35},
    {"product_id": 25, "zip_code": "682001", "velocity_score": 0.78, "units_last_hour": 28},
    {"product_id": 28, "zip_code": "682001", "velocity_score": 0.70, "units_last_hour": 20},
    {"product_id": 20, "zip_code": "682001", "velocity_score": 0.62, "units_last_hour": 16},
    {"product_id": 26, "zip_code": "682001", "velocity_score": 0.55, "units_last_hour": 11},
    {"product_id": 23, "zip_code": "682001", "velocity_score": 0.50, "units_last_hour": 9},
    {"product_id": 24, "zip_code": "682001", "velocity_score": 0.58, "units_last_hour": 14},
    {"product_id": 30, "zip_code": "682001", "velocity_score": 0.45, "units_last_hour": 7},
    # Odisha (752001)
    {"product_id": 31, "zip_code": "752001", "velocity_score": 0.90, "units_last_hour": 42},
    {"product_id": 32, "zip_code": "752001", "velocity_score": 0.82, "units_last_hour": 32},
    {"product_id": 33, "zip_code": "752001", "velocity_score": 0.78, "units_last_hour": 26},
    {"product_id": 36, "zip_code": "752001", "velocity_score": 0.72, "units_last_hour": 22},
    {"product_id": 37, "zip_code": "752001", "velocity_score": 0.68, "units_last_hour": 19},
    {"product_id": 41, "zip_code": "752001", "velocity_score": 0.65, "units_last_hour": 17},
    {"product_id": 44, "zip_code": "752001", "velocity_score": 0.60, "units_last_hour": 14},
    {"product_id": 40, "zip_code": "752001", "velocity_score": 0.55, "units_last_hour": 10},
    {"product_id": 39, "zip_code": "752001", "velocity_score": 0.75, "units_last_hour": 25},
]

# Look Completer Presets
LOOK_PRESETS = [
    {"primary_item_id": 1, "suggested_accessory_id": 124, "suggested_footwear_id": 149, "occasion_tag": "wedding_day"},
    {"primary_item_id": 2, "suggested_accessory_id": 124, "suggested_footwear_id": 149, "occasion_tag": "wedding_day"},
    {"primary_item_id": 9, "suggested_accessory_id": 127, "suggested_footwear_id": 149, "occasion_tag": "festival"},
    {"primary_item_id": 7, "suggested_accessory_id": 127, "suggested_footwear_id": None, "occasion_tag": "festival"},
    {"primary_item_id": 16, "suggested_accessory_id": 127, "suggested_footwear_id": None, "occasion_tag": "festival"},
    {"primary_item_id": 97, "suggested_accessory_id": 124, "suggested_footwear_id": 149, "occasion_tag": "wedding_day"},
    {"primary_item_id": 110, "suggested_accessory_id": 38, "suggested_footwear_id": 149, "occasion_tag": "festival"},
    {"primary_item_id": 112, "suggested_accessory_id": 135, "suggested_footwear_id": 149, "occasion_tag": "festival"},
]

# Mock Creators to seed
MOCK_CREATORS = {
    "800008": [
        {"name": "Patna Ethnic Wear Vlog", "youtube_url": "https://youtube.com/patna_ethnic", "demographic": "millennial", "subscriber_weight": 1.2, "interest_desc": "Millennial traditional saree cotton handloom ethnic daily wear"},
        {"name": "Traditional Vibes", "youtube_url": "https://youtube.com/trad_vibes", "demographic": "millennial", "subscriber_weight": 1.3, "interest_desc": "Millennial traditional saree cotton handloom ethnic daily wear"},
        {"name": "Patna Trending Now", "youtube_url": "https://youtube.com/patna_trending", "demographic": "gen-z", "subscriber_weight": 1.0, "interest_desc": "Gen-Z trendy casual ethnic kurta jeans fusion affordable Patna"},
    ],
    "682001": [
        {"name": "Kochi Couture", "youtube_url": "https://youtube.com/kochi_couture", "demographic": "millennial", "subscriber_weight": 1.3, "interest_desc": "Millennial traditional South Indian silk saree white gold cream Mundu"},
        {"name": "Fort Kochi Style", "youtube_url": "https://youtube.com/fort_kochi", "demographic": "gen-z", "subscriber_weight": 1.5, "interest_desc": "Gen-Z linen cotton summer coastal fashion modern artsy"},
    ],
    "752001": [
        {"name": "Odisha Handloom Vlog", "youtube_url": "https://youtube.com/odisha_handloom", "demographic": "millennial", "subscriber_weight": 1.2, "interest_desc": "Millennial traditional cotton saree Sambalpuri Ikat handloom ethnic Odisha"},
        {"name": "Puri Style Hub", "youtube_url": "https://youtube.com/puri_style", "demographic": "gen-z", "subscriber_weight": 1.4, "interest_desc": "Gen-Z trendy casual cotton ethnic fusion affordable Odisha temple town"},
    ]
}

# Mock Stores/Boutiques to seed
MOCK_STORES = {
    "800008": [
        {"name": "Kalyan Silks Patna", "rating": 4.6, "review_count": 1200, "estimated_cost": 2500, "description": "traditional silk saree festive ethnic heavy embroidered Patna bridal"},
        {"name": "Manyavar Patna", "rating": 4.3, "review_count": 800, "estimated_cost": 3000, "description": "festive ethnic kurta set velvet silk wedding occasion Patna"},
        {"name": "Patna Fashion House", "rating": 4.1, "review_count": 350, "estimated_cost": 1500, "description": "affordable ethnic casual cotton kurti daily wear Patna budget"},
    ],
    "682001": [
        {"name": "Kochi Silk House", "rating": 4.5, "review_count": 600, "estimated_cost": 2800, "description": "South Indian silk saree traditional Kochi elegant Kanjeevaram Kasavu"},
        {"name": "Modern Trends Kochi", "rating": 4.0, "review_count": 200, "estimated_cost": 1800, "description": "modern fusion ethnic casual daily wear affordable Kochi trendy"},
        {"name": "Coastal Chic Boutique", "rating": 4.7, "review_count": 90, "estimated_cost": 2200, "description": "breezy coastal cotton rayon casual western beach Fort Kochi summer"},
    ],
    "752001": [
        {"name": "Boyanika Odisha Handlooms", "rating": 4.7, "review_count": 950, "estimated_cost": 2000, "description": "traditional Sambalpuri cotton saree handloom Ikat Puri Odisha"},
        {"name": "Priyadarshini Handlooms", "rating": 4.5, "review_count": 400, "estimated_cost": 2800, "description": "premium traditional tussar silk Sambalpuri saree elegant Odisha"},
        {"name": "Puri Jagannath Weaves", "rating": 4.3, "review_count": 150, "estimated_cost": 1500, "description": "affordable cotton saree dhoti local traditional weave Puri budget"},
    ]
}

def seed_database():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase connection parameters not found in environment. Database seeding skipped.")
        return
        
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase client initialized successfully.")
        
        # 1. Seed Products from local_catalog.json
        try:
            if os.path.exists(LOCAL_CATALOG_FILE):
                logger.info("Seeding products from local_catalog.json...")
                with open(LOCAL_CATALOG_FILE, "r") as f:
                    products = json.load(f)
                    
                # Truncate products table first
                supabase.table("products").delete().neq("id", 0).execute()
                
                # Insert in chunks of 50
                chunk_size = 50
                for i in range(0, len(products), chunk_size):
                    chunk = products[i:i + chunk_size]
                    filtered_chunk = []
                    for p in chunk:
                        filtered_chunk.append({
                            "id": p["id"],
                            "name": p["name"],
                            "description": p.get("description"),
                            "image_url": p.get("image_url"),
                            "product_url": p.get("product_url"),
                            "tags": p.get("tags", []),
                            "zip_codes": p.get("zip_codes", []),
                            "embedding": p.get("embedding")
                        })
                    supabase.table("products").insert(filtered_chunk).execute()
                logger.info(f"Successfully seeded {len(products)} products.")
            else:
                logger.warning(f"local_catalog.json not found at {LOCAL_CATALOG_FILE}. Run embed_catalog.py first!")
        except Exception as e:
            logger.error(f"Error seeding products table (make sure schema.sql was run): {e}")

        # 2. Seed Calendar
        try:
            logger.info("Seeding calendar events...")
            supabase.table("calendar").delete().neq("zip_code", "").execute()
            supabase.table("calendar").insert(CALENDAR_PRESETS).execute()
            logger.info("Successfully seeded calendar table.")
        except Exception as e:
            logger.error(f"Error seeding calendar table: {e}")

        # 3. Seed Checkout Velocity
        try:
            logger.info("Seeding checkout velocity table...")
            supabase.table("checkout_velocity").delete().neq("zip_code", "").execute()
            supabase.table("checkout_velocity").insert(VELOCITY_PRESETS).execute()
            logger.info("Successfully seeded checkout_velocity table.")
        except Exception as e:
            logger.error(f"Error seeding checkout_velocity table: {e}")

        # 4. Seed Outfit Completer
        try:
            logger.info("Seeding look completer table...")
            supabase.table("outfit_completer").delete().neq("occasion_tag", "").execute()
            supabase.table("outfit_completer").insert(LOOK_PRESETS).execute()
            logger.info("Successfully seeded outfit_completer table.")
        except Exception as e:
            logger.error(f"Error seeding outfit_completer table: {e}")

        # 5. Seed Boutique Trends (regional_boutique_trends)
        try:
            if os.path.exists(BOUTIQUE_TRENDS_FILE):
                logger.info("Seeding boutique trends table...")
                with open(BOUTIQUE_TRENDS_FILE, "r") as f:
                    trends = json.load(f)
                supabase.table("regional_boutique_trends").delete().neq("store_id", "").execute()
                supabase.table("regional_boutique_trends").insert(trends).execute()
                logger.info("Successfully seeded regional_boutique_trends table.")
            else:
                logger.warning(f"real_trends_seed.json not found at {BOUTIQUE_TRENDS_FILE}.")
        except Exception as e:
            logger.error(f"Error seeding regional_boutique_trends table: {e}")

        # 6. Seed Creators
        try:
            logger.info("Seeding creators table...")
            supabase.table("creators").delete().neq("name", "").execute()
            creators_to_insert = []
            for zip_code, list_creators in MOCK_CREATORS.items():
                for c in list_creators:
                    vector = get_vibe_vector(c["interest_desc"])
                    creators_to_insert.append({
                        "name": c["name"],
                        "youtube_url": c["youtube_url"],
                        "demographic": c["demographic"],
                        "subscriber_weight": c["subscriber_weight"],
                        "embedding": vector,
                        "confidence_score": 0.90,
                        "zip_code": zip_code
                    })
            supabase.table("creators").insert(creators_to_insert).execute()
            logger.info("Successfully seeded creators table.")
        except Exception as e:
            logger.error(f"Error seeding creators table: {e}")

        # 7. Seed Stores
        try:
            logger.info("Seeding stores table...")
            supabase.table("stores").delete().neq("name", "").execute()
            stores_to_insert = []
            for zip_code, list_stores in MOCK_STORES.items():
                for s in list_stores:
                    vector = get_vibe_vector(s["description"])
                    stores_to_insert.append({
                        "name": s["name"],
                        "rating": s["rating"],
                        "review_count": s["review_count"],
                        "estimated_cost": s["estimated_cost"],
                        "embedding": vector,
                        "zip_code": zip_code
                    })
            supabase.table("stores").insert(stores_to_insert).execute()
            logger.info("Successfully seeded stores table.")
        except Exception as e:
            logger.error(f"Error seeding stores table: {e}")

        logger.info("Seeder execution phase finished.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")

if __name__ == "__main__":
    seed_database()
