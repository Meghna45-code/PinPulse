import os
import sys
import json
import time
import logging
from datetime import datetime
import numpy as np
import holidays
from dotenv import load_dotenv
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_enriched_environment")

# Load environment
load_dotenv("backend/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found in environment!")
    sys.exit(1)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

WEATHER_PRESETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "app", "weather_presets.json"))
CALENDAR_PRESETS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "app", "calendar_presets.json"))

ZIP_MAPPING = {
    "800008": {"subdiv": "BR", "city": "Patna", "state": "Bihar"},
    "682001": {"subdiv": "KL", "city": "Kochi", "state": "Kerala"},
    "752001": {"subdiv": "OD", "city": "Puri", "state": "Odisha"}
}

# Baseline Weather averages for each location (1-12 months)
WEATHER_BASELINES = {
    "800008": { # Patna
        1: {"desc": "Cold & Foggy ❄️", "temp": "10°C–22°C", "cold_wave": True, "hot_wave": False, "rainy": False, "weather_conditions": "cold"},
        2: {"desc": "Cool & Sunny 🌤️", "temp": "12°C–26°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "cold"},
        3: {"desc": "Warming Up ☀️", "temp": "17°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        4: {"desc": "Hot & Dry 🔥", "temp": "21°C–38°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_dry"},
        5: {"desc": "Very Hot 🔥", "temp": "24°C–39°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_dry"},
        6: {"desc": "Hot & Humid 🌡️", "temp": "25°C–35°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        7: {"desc": "Hot & Monsoon 🌧️", "temp": "26°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        8: {"desc": "Humid & Wet 🌧️", "temp": "25°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        9: {"desc": "Post-Monsoon Humidity 🌧️", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        10: {"desc": "Pleasant & Sunny 🍂", "temp": "20°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        11: {"desc": "Cool & Dry 🍂", "temp": "15°C–27°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        12: {"desc": "Cold & Dry ❄️", "temp": "11°C–23°C", "cold_wave": True, "hot_wave": False, "rainy": False, "weather_conditions": "cold"}
    },
    "682001": { # Fort Kochi
        1: {"desc": "Pleasant & Breezy 🍃", "temp": "23°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        2: {"desc": "Breezy & Warm 🍃", "temp": "24°C–32°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        3: {"desc": "Warm & Sunny ☀️", "temp": "25°C–33°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "hot_humid"},
        4: {"desc": "Warm & Dry ☀️", "temp": "27°C–33°C", "cold_wave": False, "hot_wave": True, "rainy": False, "weather_conditions": "hot_humid"},
        5: {"desc": "Pre-Monsoon Showers 🌧️", "temp": "27°C–31°C", "cold_wave": False, "hot_wave": True, "rainy": True, "weather_conditions": "hot_humid"},
        6: {"desc": "Cool & Rainy 🌧️", "temp": "26°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        7: {"desc": "Monsoon Breezes 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        8: {"desc": "Cloudy & Rainy 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        9: {"desc": "Pleasant Showers 🌧️", "temp": "25°C–29°C", "cold_wave": False, "hot_wave": False, "rainy": True, "weather_conditions": "hot_humid"},
        10: {"desc": "Cool & Pleasant 🍂", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "hot_humid"},
        11: {"desc": "Cool & Cozy 🍃", "temp": "25°C–30°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"},
        12: {"desc": "Pleasant Winter ❄️", "temp": "24°C–31°C", "cold_wave": False, "hot_wave": False, "rainy": False, "weather_conditions": "warm_moderate"}
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

# Core curated events (always seed if not already present)
CORE_PRESETS = [
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

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
         logger.warning("Supabase environment variables not found.")
         return None
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        logger.error(f"Error loading Supabase: {e}")
        return None

def call_gemini_enrich_event(event_name, date_str, location_name):
    """Query Gemini to generate custom local attire tags, event type, and festive logic."""
    prompt = f"""
    You are a regional Indian fashion stylist.
    Analyze the holiday: "{event_name}" occurring on "{date_str}" in the location "{location_name}".
    
    Translate this event into structured styling parameters.
    Return a valid JSON object matching this schema:
    {{
       "event_type": "Must be one of: 'festival' (for regional/national festivals/holidays), 'wedding_day', or 'casual'",
       "is_festive": true or false,
       "attire_tags": ["A list of 4-6 lowercase apparel tags suitable for this event and region (e.g., 'cotton', 'white', 'saree', 'kurta', 'khadi', 'formal', 'ethnic', 'linen', 'silk', 'pastel'). Focus on regional tradition, colors, and comfort."]
    }}
    """
    try:
        model = genai.GenerativeModel('models/gemini-flash-lite-latest')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        data = json.loads(text)
        return data
    except Exception as e:
        logger.warning(f"Failed to enrich event {event_name} via Gemini: {e}")
        return None

def call_gemini_enrich_weather(city, month, temp_range, condition):
    """Query Gemini to return allowable materials and styling vibes for specific monthly weather conditions."""
    prompt = f"""
    The monthly average weather for {city} in Month {month} is:
    - Temperature Range: {temp_range}
    - Conditions: {condition}
    
    Determine the optimal fabric materials suitable for these weather conditions to ensure comfort and breathability.
    Return a valid JSON object matching this schema:
    {{
       "allowable_materials": ["A list of 3-5 fabrics/materials suited for this weather (e.g., 'cotton', 'linen', 'rayon' for hot/humid, or 'wool', 'velvet', 'fleece', 'leather', 'denim' for cold). Use lowercase."]
    }}
    """
    try:
        model = genai.GenerativeModel('models/gemini-flash-lite-latest')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Failed to enrich weather for Month {month} in {city}: {e}")
        return None

def main():
    sb = get_supabase_client()
    existing_events = {}

    if sb:
        try:
            logger.info("Fetching existing calendar rows from Supabase...")
            res = sb.table("calendar").select("*").execute()
            for row in res.data:
                key = (row["zip_code"], str(row["date"]))
                existing_events[key] = row
            logger.info(f"Loaded {len(existing_events)} existing events from Supabase.")
        except Exception as e:
            logger.error(f"Error reading calendar table: {e}")

    # Build local candidate calendar list (starting with our Core Presets)
    candidates = {}
    for ev in CORE_PRESETS:
        key = (ev["zip_code"], ev["date"])
        candidates[key] = ev

    # Append official national & state holidays using Python holidays library
    logger.info("Retrieving official state-specific public holidays for 2026...")
    for zip_code, info in ZIP_MAPPING.items():
        subdiv = info["subdiv"]
        city = info["city"]
        state = info["state"]
        
        # Instantiate holidays
        state_holidays = holidays.India(subdiv=subdiv, years=2026)
        for date_obj, name in state_holidays.items():
            date_str = date_obj.strftime("%Y-%m-%d")
            key = (zip_code, date_str)
            
            # Skip if it is already in our existing DB table to preserve manual edits/custom fields
            if key in existing_events:
                logger.info(f"  [Preserved] {name} on {date_str} in {city} (already exists in DB)")
                continue
                
            # If not in existing, add/merge candidate
            if key not in candidates:
                candidates[key] = {
                    "zip_code": zip_code,
                    "date": date_str,
                    "event_name": name,
                    "event_type": "festival", # Default, LLM will refine
                    "attire_tags": [],
                    "is_festive": True
                }

    # Now, process candidates and run LLM calls for new/missing tags
    logger.info(f"Processing candidate events (Total unique date-zip pairs: {len(candidates)})...")
    final_calendar = []
    
    # Track the API request limit: 15 per minute max
    call_delay = 4.1

    for key, ev in candidates.items():
        zip_code, date_str = key
        city = ZIP_MAPPING[zip_code]["city"]
        
        # If this event exists in Supabase, keep it exactly as is
        if key in existing_events:
            final_calendar.append(existing_events[key])
            continue

        # Otherwise, run LLM enrichment for the new entry!
        logger.info(f"  [New Holiday] Enriching '{ev['event_name']}' on {date_str} in {city}...")
        llm_enrichment = call_gemini_enrich_event(ev["event_name"], date_str, city)
        
        if llm_enrichment:
            ev["event_type"] = llm_enrichment.get("event_type", "festival")
            ev["is_festive"] = llm_enrichment.get("is_festive", True)
            ev["attire_tags"] = llm_enrichment.get("attire_tags", ["ethnic", "formal"])
            logger.info(f"    -> Enriched Tags: {ev['attire_tags']}")
        else:
            # Fallback if LLM fails
            ev["attire_tags"] = ["ethnic", "formal", "casual"]

        final_calendar.append(ev)
        time.sleep(call_delay)

    # Sync calendar table back to Supabase
    if sb:
        try:
            logger.info("Upserting calendar entries to Supabase...")
            # Upsert chunked
            chunk_size = 50
            for i in range(0, len(final_calendar), chunk_size):
                chunk = final_calendar[i:i + chunk_size]
                sb.table("calendar").upsert(chunk).execute()
            logger.info(f"Successfully upserted {len(final_calendar)} events to calendar table in Supabase.")
        except Exception as e:
            logger.error(f"Error upserting to Supabase: {e}")

    # Write copy to local fallback file
    try:
        with open(CALENDAR_PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(final_calendar, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved calendar fallback presets to {CALENDAR_PRESETS_FILE}")
    except Exception as e:
        logger.error(f"Error writing calendar file: {e}")

    # --- Process and Enrich Weather presets ---
    logger.info("Processing weather matrix enrichment...")
    enriched_weather = {}

    for zip_code, months in WEATHER_BASELINES.items():
        city = ZIP_MAPPING[zip_code]["city"]
        enriched_weather[zip_code] = {}
        
        for month, data in months.items():
            logger.info(f"  Enriching weather for Month {month} in {city}...")
            llm_w = call_gemini_enrich_weather(city, month, data["temp"], data["desc"])
            
            if llm_w:
                data["allowable_materials"] = llm_w.get("allowable_materials", ["cotton", "linen"])
                logger.info(f"    -> Materials: {data['allowable_materials']}")
            else:
                data["allowable_materials"] = ["cotton", "linen"]
                
            enriched_weather[zip_code][str(month)] = data
            time.sleep(call_delay)

    # Write weather presets locally
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(WEATHER_PRESETS_FILE), exist_ok=True)
        with open(WEATHER_PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(enriched_weather, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved enriched weather presets to {WEATHER_PRESETS_FILE}")
    except Exception as e:
        logger.error(f"Error writing weather presets file: {e}")

    logger.info("Environment Seeder completed successfully!")

if __name__ == "__main__":
    main()
