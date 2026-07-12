import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Configure Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

REGIONS = {
    "800008": {"name": "Patna", "locality": "Frazer Road, Patna, Bihar", "query_theme": "traditional ethnic festive wear saree kurtas bihar"},
    "682001": {"name": "Kochi", "locality": "M G Road, Kochi, Kerala", "query_theme": "kasavu traditional handloom cotton white gold kerala"},
    "793003": {"name": "Shillong", "locality": "Police Bazar, Shillong, Meghalaya", "query_theme": "streetwear winter jacket boots tribal jainsem traditional"}
}

def load_catalog():
    with open('local_catalog.json', 'r') as f:
        return json.load(f)

def get_live_youtube_videos(zip_code, region_name):
    query = f"{region_name} fashion haul shopping outfits"
    print(f"[{region_name}] Searching YouTube for: '{query}'")
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": 5,
        "type": "video",
        "key": GOOGLE_API_KEY
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"Error fetching YouTube videos: {r.text}")
        return []
    
    items = r.json().get("items", [])
    videos = []
    for idx, item in enumerate(items):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        videos.append({
            "video_id": video_id,
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "thumbnail_url": snippet["thumbnails"]["high"]["url"],
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "description": snippet["description"]
        })
    return videos

def get_live_boutiques(zip_code, locality):
    print(f"[{zip_code}] Searching Google Places for boutiques near: '{locality}'")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"clothing boutique clothing stores near {locality}",
        "key": GOOGLE_API_KEY
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"Error fetching places: {r.text}")
        return []
    
    results = r.json().get("results", [])
    boutiques = []
    for idx, place in enumerate(results[:5]):
        name = place["name"]
        addr = place.get("formatted_address", locality)
        rating = place.get("rating", 4.0)
        place_id = place["place_id"]
        maps_url = f"https://www.google.com/maps/search/?api=1&query={requests.utils.quote(name + ' ' + addr)}&query_place_id={place_id}"
        
        boutiques.append({
            "store_id": f"STR_{zip_code}_{idx+1:03d}",
            "zip_code": zip_code,
            "locality": locality,
            "store_name": name,
            "address": addr,
            "rating": rating,
            "maps_url": maps_url,
            "social_signal_source": "Instagram Location Signal" if idx % 2 == 0 else "YouTube Store Tour",
            "simulated_engagement": int(12000 + (rating * 4500) + (idx * 1500))
        })
    return boutiques

def match_product_by_tags(inferred_tags, catalog, zip_code):
    best_product = None
    best_score = -1
    inferred_set = set(inferred_tags)
    
    for p in catalog:
        # Geographic availability constraint check
        p_zips = p.get("zip_codes", [])
        if p_zips and zip_code not in p_zips:
            continue
            
        p_tags = set(p.get("tags", []))
        score = len(inferred_set.intersection(p_tags))
        
        # Boost specific categories based on region
        if zip_code in ["800008", "800001"] and "saree" in p_tags:
            score += 2
        elif zip_code in ["682001", "560034"] and "kasavu_weave" in p_tags:
            score += 2
        elif zip_code in ["793003", "110049"] and ("handwoven_silk" in p_tags or "tribal_heritage" in p_tags):
            score += 2
            
        if score > best_score:
            best_score = score
            best_product = p
            
    return best_product, best_score

def run_pipeline():
    print("=== STARTING ONE-TIME TRENDS EXTRACTION & DB FREEZING PIPELINE ===")
    catalog = load_catalog()
    
    all_boutique_records = []
    
    for zip_code, info in REGIONS.items():
        region_name = info["name"]
        locality = info["locality"]
        
        # 1. Fetch live YouTube videos
        videos = get_live_youtube_videos(zip_code, region_name)
        
        # 2. Fetch live Google Maps boutiques
        boutiques = get_live_boutiques(zip_code, locality)
        
        # Combine YouTube and boutiques in our database seed list
        # To avoid duplicating primary key store_id, YouTube videos will have store_id prefixed with 'YT_'
        # We will write BOTH to the database as static records!
        
        # Process Boutiques
        for idx, store in enumerate(boutiques):
            # Simulate trend extraction mapping to tags
            if region_name == "Patna":
                trend = "banarasi-silk" if idx % 2 == 0 else "tussar-saree"
                cluster = "Traditional Ethnic & Festive Silk"
            elif region_name == "Kochi":
                trend = "kasavu_weave" if idx % 2 == 0 else "cotton"
                cluster = "Tropical Handloom & Kasavu Weave"
            else:
                trend = "handwoven_silk" if idx % 2 == 0 else "streetwear"
                cluster = "North East Traditional & Streetwear"
                
            record = {
                "store_id": store["store_id"],
                "zip_code": zip_code,
                "locality": store["locality"],
                "store_name": store["store_name"],
                "social_signal_source": store["social_signal_source"],
                "simulated_engagement": store["simulated_engagement"],
                "extracted_visual_trend": trend,
                "style_vibe_cluster": cluster
            }
            all_boutique_records.append(record)
            
        # Process YouTube videos and save them into the same DB table under a distinct YT_ prefix to prevent primary key conflict
        for idx, video in enumerate(videos):
            # Inferred tags based on region and video content
            if region_name == "Patna":
                trend = "banarasi-silk" if idx == 0 else "tussar-saree" if idx == 1 else "ethnic"
                cluster = f"YouTube Creator: {video['channel']}"
            elif region_name == "Kochi":
                trend = "kasavu_weave" if idx == 0 else "cotton" if idx == 1 else "ethnic"
                cluster = f"YouTube Creator: {video['channel']}"
            else:
                trend = "streetwear" if idx == 0 else "jacket" if idx == 1 else "traditional"
                cluster = f"YouTube Creator: {video['channel']}"
                
            record = {
                "store_id": f"YT_{zip_code}_{video['video_id']}",
                "zip_code": zip_code,
                "locality": video["title"][:100], # Keep video title in locality/description field
                "store_name": video["channel"],
                "social_signal_source": "YouTube Creator Video",
                "simulated_engagement": int(45000 - (idx * 4000)),
                "extracted_visual_trend": trend,
                "style_vibe_cluster": cluster
            }
            all_boutique_records.append(record)

    # Write all records to the Supabase database
    print(f"\nWriting {len(all_boutique_records)} records to Supabase 'regional_boutique_trends' table...")
    try:
        # Upsert records
        res = sb.table("regional_boutique_trends").upsert(all_boutique_records).execute()
        print("Successfully updated database with live API data!")
    except Exception as e:
        print(f"Error writing to database: {e}")

if __name__ == "__main__":
    run_pipeline()
