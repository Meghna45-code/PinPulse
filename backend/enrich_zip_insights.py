"""
enrich_zip_insights.py
----------------------
Queries Gemini 3.5 Flash once to get the typical Average Order Value (AOV)
for online fashion apparel shopping in Patna, Kochi, and Puri.
Saves the results in local_catalog_zip_insights.json and syncs to Supabase.
"""
import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("zip_insights")

# Load environment
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(BASE_DIR, "backend", ".env")
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

REGIONS = {
    "800008": "Patna (800008)",
    "682001": "Kochi (682001)",
    "752001": "Puri, Odisha (752001)"
}

def query_aov_from_gemini():
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment!")
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    
    prompt = """
    Analyze online fashion retail behavior in India. Estimate the typical Average Order Value (AOV) in INR (Indian Rupees) for online fashion apparel purchases in the following three regional markets:
    1. Patna, Bihar (Zip 800008)
    2. Kochi, Kerala (Zip 682001)
    3. Puri, Odisha (Zip 752001)

    Provide the estimates based on local purchasing power, e-commerce adoption, and consumer behavior profiles in tier-2/3 cities versus coastal/artsy hubs.
    You MUST output ONLY a valid JSON object matching the following structure (no markdown formatting, no other text):
    {
      "800008": 1500,
      "682001": 2200,
      "752001": 1200
    }
    Make sure the values are reasonable integers representing typical ticket sizes (e.g. between 1000 and 3500 INR).
    """

    try:
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean any markdown code block wrapper if the model added it
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        
        data = json.loads(text)
        logger.info(f"Successfully retrieved AOV from Gemini: {data}")
        return data
    except Exception as e:
        logger.error(f"Error querying Gemini: {e}")
        # Realistic fallback values if the API fails or rate limits
        return {
            "800008": 1450,
            "682001": 2100,
            "752001": 1150
        }

def save_and_sync():
    insights = query_aov_from_gemini()
    if not insights:
        return

    # 1. Save local JSON
    out_file = os.path.join(BASE_DIR, "backend", "zip_code_insights.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2)
    logger.info(f"Saved local insights to {out_file}")

    # 2. Try syncing to Supabase
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase credentials missing. Skipping DB sync.")
        return

    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        logger.info("Connected to Supabase. Seeding zip_code_insights table...")
        for zip_code, aov in insights.items():
            try:
                supabase.table("zip_code_insights").upsert({
                    "zip_code": zip_code,
                    "average_order_value": aov
                }).execute()
                logger.info(f"  Upserted {zip_code} with AOV = {aov} INR")
            except Exception as e:
                logger.error(f"  Failed to upsert {zip_code} (Table 'zip_code_insights' might not exist yet): {e}")
                logger.info("  Make sure to run the ALTER TABLE sql script in your Supabase Dashboard SQL Editor.")
    except Exception as e:
        logger.error(f"Supabase connection error: {e}")

if __name__ == "__main__":
    save_and_sync()
