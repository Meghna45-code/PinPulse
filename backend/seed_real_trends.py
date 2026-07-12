import os
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_real_trends")

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# The 18 Real Boutiques directory mapping to their Zip Codes and extracted visual trends
real_boutiques = [
    # 560034 - Koramangala, Bengaluru
    {
        "store_id": "STR_560034_001",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "Fulki Boutique",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 32000,
        "extracted_visual_trend": "y2k-crop",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },
    {
        "store_id": "STR_560034_002",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "The Budget Boutique",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 21000,
        "extracted_visual_trend": "baggy-jeans",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },
    {
        "store_id": "STR_560034_003",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "Style Union",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 45000,
        "extracted_visual_trend": "oversized-tees",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },
    {
        "store_id": "STR_560034_004",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "Shabnam Boutique",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 15000,
        "extracted_visual_trend": "cargo-pants",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },
    {
        "store_id": "STR_560034_005",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "Trends Footwear",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 18500,
        "extracted_visual_trend": "varsity-jackets",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },
    {
        "store_id": "STR_560034_006",
        "zip_code": "560034",
        "locality": "Koramangala, Bengaluru",
        "store_name": "Urban Retro Studio",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 27000,
        "extracted_visual_trend": "y2k-crop",
        "style_vibe_cluster": "Streetwear & Gen-Z Casual"
    },

    # 110049 - South Ext, New Delhi
    {
        "store_id": "STR_110049_001",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "QBIK Boutique",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 42000,
        "extracted_visual_trend": "indo-western-gown",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },
    {
        "store_id": "STR_110049_002",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "Aza Fashions",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 39000,
        "extracted_visual_trend": "pastel-lehenga",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },
    {
        "store_id": "STR_110049_003",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "Frontier Raas",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 48000,
        "extracted_visual_trend": "pastel-lehenga",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },
    {
        "store_id": "STR_110049_004",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "Monika & Nidhi",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 29000,
        "extracted_visual_trend": "chikankari-kurti",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },
    {
        "store_id": "STR_110049_005",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "Ritu Kumar",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 31500,
        "extracted_visual_trend": "designer-dupatta",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },
    {
        "store_id": "STR_110049_006",
        "zip_code": "110049",
        "locality": "South Ext, New Delhi",
        "store_name": "KALKI Fashion",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 44000,
        "extracted_visual_trend": "indo-western-gown",
        "style_vibe_cluster": "Premium Fusion & Indo-Western"
    },

    # 800001 - Frazer Road, Patna
    {
        "store_id": "STR_800001_001",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Rap&Chik Designer Studio",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 24000,
        "extracted_visual_trend": "banarasi-silk",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    },
    {
        "store_id": "STR_800001_002",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Vachi Boutique",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 19500,
        "extracted_visual_trend": "tussar-saree",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    },
    {
        "store_id": "STR_800001_003",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Bridal Zone",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 31000,
        "extracted_visual_trend": "heavy-anarkali",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    },
    {
        "store_id": "STR_800001_004",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Vandana Couture",
        "social_signal_source": "YouTube Shopping Haul",
        "simulated_engagement": 28000,
        "extracted_visual_trend": "festive-kurta-set",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    },
    {
        "store_id": "STR_800001_005",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Bandhan Boutique",
        "social_signal_source": "Instagram Post Location",
        "simulated_engagement": 22000,
        "extracted_visual_trend": "banarasi-silk",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    },
    {
        "store_id": "STR_800001_006",
        "zip_code": "800001",
        "locality": "Frazer Road, Patna",
        "store_name": "Janvi’s Closet",
        "social_signal_source": "Instagram Reel Tag",
        "simulated_engagement": 17000,
        "extracted_visual_trend": "tussar-saree",
        "style_vibe_cluster": "Traditional Ethnic & Festive Silk"
    }
]

def seed_database():
    # Save locally first
    seed_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "real_trends_seed.json"))
    with open(seed_file_path, "w") as f:
        json.dump(real_boutiques, f, indent=4)
    logger.info(f"Successfully saved {len(real_boutiques)} store profiles locally to {seed_file_path}")

    # Now attempt to seed Supabase
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase credentials missing. Seeding only completed locally.")
        return

    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        logger.info("Checking connection to Supabase and seeding regional boutique trends...")
        
        # Clear existing entries in regional_boutique_trends
        try:
            supabase.table("regional_boutique_trends").delete().neq("store_id", "").execute()
            logger.info("Cleared existing entries from 'regional_boutique_trends'.")
        except Exception as delete_error:
            logger.warning(f"Could not clear table (it might not exist yet): {delete_error}")
            logger.info("Attempting to insert records. If this fails, make sure you created the table in Supabase first.")
        
        # Bulk Insert
        res = supabase.table("regional_boutique_trends").insert(real_boutiques).execute()
        logger.info(f"✅ Successfully seeded {len(res.data)} real boutique trends to Supabase!")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed Supabase: {e}")
        logger.error("IMPORTANT: Make sure you have created the 'regional_boutique_trends' table in your Supabase SQL editor using the schema in backend/schema.sql!")

if __name__ == "__main__":
    seed_database()
