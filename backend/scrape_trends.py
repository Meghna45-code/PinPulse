import os
import json
import logging
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("scrape_trends")

# Load environment variables
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "youtube_cache.json")

# Core dates we want to cache trends for
DATE_PROFILES = {
    "aug_15": {
        "query": "daily cotton outfit ideas summer styles india",
        "mock_trends": ["cotton", "linen", "dailywear", "kurtas", "casuals", "breathable", "pastel", "summer-fashion"],
        "description": "Baseline trends: Everyday lightweight, breathable cottons and casual pastel styles suitable for humid summer weather."
    },
    "nov_2": {
        "query": "chhath puja saree styling heavy festive traditional wear bihar",
        "mock_trends": ["silk", "zari", "festive", "saree", "chhath-puja", "traditional", "ethnic", "banarasi", "gota-patti"],
        "description": "Festive Surge trends: Shifting focus to heavy traditional silks, Banarasi sarees, Zari embroidery, and vibrant festival ethnic wear ahead of Chhath Puja."
    },
    "jan_5": {
        "query": "winter styling velvet suits shawls cold wave fashion india",
        "mock_trends": ["velvet", "shawl", "winter", "cardigan", "hoodie", "jacket", "thermal", "puffer", "cashmere", "heavy-weight"],
        "description": "Climate Surge trends: Cold wave fashion boosting heavy velvets, thermal layers, puffer jackets, shawls, and dark warm tones."
    }
}

def fetch_youtube_tags(query: str, max_results: int = 10) -> list:
    """
    Fetches video tags from the official YouTube Data API.
    Uses search endpoint to find videos, then videos endpoint to retrieve tags.
    """
    if not YOUTUBE_API_KEY:
        logger.warning("No YOUTUBE_API_KEY found in .env. Skipping API request.")
        return []

    try:
        # Step 1: Search for relevant video IDs
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            "part": "snippet",
            "q": query,
            "maxResults": max_results,
            "type": "video",
            "key": YOUTUBE_API_KEY
        }
        
        logger.info(f"Searching YouTube videos for: '{query}'")
        search_response = requests.get(search_url, params=search_params)
        
        if search_response.status_code != 200:
            logger.error(f"YouTube Search failed with code {search_response.status_code}: {search_response.text}")
            return []
            
        search_data = search_response.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", []) if "id" in item and "videoId" in item["id"]]
        
        if not video_ids:
            logger.warning("No videos found matching query.")
            return []

        # Step 2: Fetch detailed info (including tags) for those videos
        videos_url = "https://www.googleapis.com/youtube/v3/videos"
        videos_params = {
            "part": "snippet,topicDetails",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY
        }
        
        logger.info(f"Fetching tags for {len(video_ids)} videos...")
        videos_response = requests.get(videos_url, params=videos_params)
        
        if videos_response.status_code != 200:
            logger.error(f"YouTube Videos query failed with code {videos_response.status_code}: {videos_response.text}")
            return []
            
        videos_data = videos_response.json()
        
        # Aggregate tags
        extracted_tags = []
        for item in videos_data.get("items", []):
            snippet = item.get("snippet", {})
            # Read snippet tags
            video_tags = snippet.get("tags", [])
            for t in video_tags:
                tag_lower = t.lower().strip()
                if tag_lower and tag_lower not in extracted_tags:
                    extracted_tags.append(tag_lower)
            
            # Read categories/topicDetails as fallbacks
            topic_details = item.get("topicDetails", {})
            relevant_categories = topic_details.get("topicCategories", [])
            for cat in relevant_categories:
                # Topic categories are URLs like 'https://en.wikipedia.org/wiki/Fashion'
                cat_name = cat.split("/")[-1].lower().replace("_", "-")
                if cat_name not in extracted_tags:
                    extracted_tags.append(cat_name)

        logger.info(f"Successfully extracted {len(extracted_tags)} unique tags from YouTube API.")
        return extracted_tags

    except Exception as e:
        logger.error(f"Error calling YouTube API: {e}")
        return []

def main():
    logger.info("Initializing YouTube Trend Radar Scraper...")
    cache_data = {}
    
    # Check if existing cache exists
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
            logger.info("Loaded existing trend cache.")
        except Exception:
            logger.warning("Existing cache file is corrupted. Re-creating.")

    for profile_key, profile_info in DATE_PROFILES.items():
        logger.info(f"Processing Profile: '{profile_key}'...")
        
        # Try fetching real data
        api_tags = fetch_youtube_tags(profile_info["query"])
        
        if api_tags:
            # We got real tags! Merge with mock tags to ensure catalog matches will succeed
            final_tags = list(set(api_tags + profile_info["mock_trends"]))
            logger.info(f"Profile '{profile_key}': Using {len(final_tags)} API-scraped + core tags.")
        else:
            # Fall back to high-fidelity mock trends
            final_tags = profile_info["mock_trends"]
            logger.info(f"Profile '{profile_key}': YouTube API key missing or query failed. Falling back to pre-defined trends: {final_tags}")
            
        cache_data[profile_key] = {
            "query": profile_info["query"],
            "trends": final_tags,
            "description": profile_info["description"]
        }

    # Write back to cache file
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=4)
        logger.info(f"Successfully saved all trend profiles to {CACHE_FILE}")
    except Exception as e:
        logger.error(f"Failed to write cache file: {e}")

if __name__ == "__main__":
    main()
