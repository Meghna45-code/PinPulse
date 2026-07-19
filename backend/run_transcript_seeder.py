import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Import get_vibe_vector from embed_catalog for embedding compatibility
import sys
sys.path.append(os.path.dirname(__file__))
from embed_catalog import get_vibe_vector

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_transcript_seeder")

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.error("GEMINI_API_KEY not found in environment!")

def get_transcript(video_id):
    """Pulls text transcript from YouTube using the transcript API."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return full_text
    except Exception as e:
        logger.error(f"Failed to fetch transcript for video ID {video_id}: {e}")
        return None

def extract_fashion_data(transcript_text, is_creator=True, pincode="800008"):
    """Uses Gemini to clean and extract fashion metadata from the transcript text."""
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not configured. Skipping LLM call.")
        return None

    if is_creator:
        prompt = f"""
You are an AI fashion extractor. Read this raw video transcript from a local lifestyle creator.
Extract the outfit they are wearing or discussing. Ignore non-fashion talk.
Return ONLY a valid JSON object (no markdown wrapping, no ```json formatting) in this format:
{{
  "source": "creator",
  "pincode": "{pincode}",
  "item": "[e.g., oversized graphic tee]",
  "fabric": "[e.g., cotton]",
  "color": "[e.g., black]",
  "vibe": "[e.g., casual street style]",
  "occasion": "[e.g., college wear]"
}}

Transcript:
{transcript_text}
"""
    else:
        prompt = f"""
You are an AI retail inventory extractor. Read this raw transcript from a local physical store or market tour.
Extract the new clothing inventory they are showing. Identify the store name if mentioned.
Return ONLY a valid JSON object (no markdown wrapping, no ```json formatting) in this format:
{{
  "source": "boutique",
  "pincode": "{pincode}",
  "store_name": "[e.g., Khetan Market / Unknown]",
  "item": "[e.g., Chikankari Kurti]",
  "fabric": "[e.g., Georgette]",
  "color": "[e.g., Pastel Green]",
  "inventory_status": "new arrival"
}}

Transcript:
{transcript_text}
"""

    try:
        model = genai.GenerativeModel('models/gemini-flash-lite-latest')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean any accidental markdown block markers if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
            if text.startswith("json"):
                text = text[4:].strip()
                
        return json.loads(text)
    except Exception as e:
        logger.error(f"Error parsing fashion details with Gemini: {e}")
        return None

def process_seeding_from_excel(excel_path):
    """Ingests Excel list, downloads transcripts, cleans them, and vectorizes."""
    if not os.path.exists(excel_path):
        logger.error(f"Excel file not found at: {excel_path}")
        return

    logger.info(f"Loading seed inputs from: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Expected columns: video_id, pincode, type ('creator' or 'boutique'), store_name (optional)
    results = []

    for index, row in df.iterrows():
        video_id = str(row.get('video_id', '')).strip()
        pincode = str(row.get('pincode', '800008')).strip()
        feed_type = str(row.get('type', 'creator')).strip().lower()
        store_name = str(row.get('store_name', 'Unknown')).strip()
        
        if not video_id or video_id == 'nan':
            continue

        logger.info(f"Processing ({feed_type}) Video ID: {video_id} for pincode {pincode}")
        
        # 1. Ingest transcript
        transcript = get_transcript(video_id)
        if not transcript:
            continue
            
        # 2. Extract structured details via LLM
        is_creator = (feed_type == "creator")
        clean_meta = extract_fashion_data(transcript, is_creator=is_creator, pincode=pincode)
        if not clean_meta:
            continue

        # 3. Generate 512-dimension vector embedding using the same logic as catalog
        tags = [clean_meta.get("item", ""), clean_meta.get("vibe", ""), clean_meta.get("fabric", ""), clean_meta.get("color", "")]
        tags = [t.lower() for t in tags if t]
        
        category = "festive" if "festive" in clean_meta.get("vibe", "").lower() else "casual"
        aesthetic = clean_meta.get("vibe", "casual")
        
        vector = get_vibe_vector(tags=tags, category_str=category, aesthetic_str=aesthetic)

        # 4. Construct DB record
        record_id = f"{pincode}_{feed_type}_{video_id}"
        record = {
            "id": record_id,
            "type": feed_type,
            "pincode": pincode,
            "metadata": clean_meta,
            "vector": vector
        }
        
        if not is_creator:
            record["store_name"] = clean_meta.get("store_name", store_name)
            
        results.append(record)

    # Write output to final json
    output_path = os.path.join(os.path.dirname(__file__), "pinpulse_mock_db.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    logger.info(f"Seeding completed successfully! Exported {len(results)} items to {output_path}")

if __name__ == "__main__":
    # If file path not passed, check default expected file path in workspace root
    excel_input = sys.argv[1] if len(sys.argv) > 1 else "pinpulse_youtube_seed.xlsx"
    process_seeding_from_excel(excel_input)
