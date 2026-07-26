"""
PinPulse Festival & Event Banner Engine with 14-Day Cycle Visibility Rule
"""
import os
import sys
import json
import numpy as np
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from clip_service import get_vibe_vector
from scoring_engine import cosine_similarity, normalize_cosine_score

JSON_FILE = "real_local_catalog.json"

EVENTS_REGISTRY = [
    {
        "event_id": "EVT_800008_CHHATH",
        "event_name": "Chhath Puja",
        "event_type": "local_festival",
        "pincode": "800008",
        "region": "Patna, Bihar",
        "start_date": "2026-11-15",
        "end_date": "2026-11-18",
        "visual_query": "Women's traditional silk saree in bright yellow or saffron color with zari borders",
        "banner_title": "Chhath Puja Mahaparv Collection",
        "banner_subtitle": "Pristine Red & Yellow Silk Sarees for Sandhya & Usha Arghya",
        "banner_theme_color": "#E65100"
    },
    {
        "event_id": "EVT_682001_ONAM",
        "event_name": "Onam Festival",
        "event_type": "local_festival",
        "pincode": "682001",
        "region": "Kochi, Kerala",
        "start_date": "2026-08-27",
        "end_date": "2026-08-29",
        "visual_query": "Women's cream-colored draped fabric with solid gold metallic borders",
        "banner_title": "Onam Thiruvonam Golden Kasavu",
        "banner_subtitle": "Traditional Cream & Gold Kasavu Sarees with Zari Borders",
        "banner_theme_color": "#FBC02D"
    },
    {
        "event_id": "EVT_302001_GANGAUR",
        "event_name": "Royal Gangaur Festival",
        "event_type": "local_festival",
        "pincode": "302001",
        "region": "Jaipur, Rajasthan",
        "start_date": "2026-04-04",
        "end_date": "2026-04-05",
        "visual_query": "Women's heavy traditional Indian skirt and blouse with intricate gold embroidery and vibrant red dye",
        "banner_title": "Royal Gangaur Festive Splendor",
        "banner_subtitle": "Rajputi Poshaks & Heavy Gota Patti Bandhani Lehengas",
        "banner_theme_color": "#C2185B"
    },
    {
        "event_id": "EVT_752001_NUAKHAI",
        "event_name": "Nuakhai Agricultural Harvest Festival",
        "event_type": "local_festival",
        "pincode": "752001",
        "region": "Puri, Odisha",
        "start_date": "2026-09-15",
        "end_date": "2026-09-16",
        "visual_query": "Women's handloom cotton garment featuring traditional geometric ikat weaving patterns in earthy tones",
        "banner_title": "Nuakhai Harvest Festival Collection",
        "banner_subtitle": "Authentic Sambalpuri Handloom & Bomkai Silk Weaves",
        "banner_theme_color": "#EF6C00"
    }
]

def calculate_14_day_cycle(start_date_str, end_date_str):
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")
    duration = (end_dt - start_dt).days + 1
    pre_event_days = 14 - duration
    banner_start_dt = start_dt - timedelta(days=pre_event_days)
    banner_end_dt = end_dt
    return {
        "duration_days": duration,
        "pre_event_days": pre_event_days,
        "banner_visibility_start": banner_start_dt.strftime("%Y-%m-%d"),
        "banner_visibility_end": banner_end_dt.strftime("%Y-%m-%d")
    }

def run_banner_engine():
    print("Loading catalog...")
    catalog_path = os.path.join(os.path.dirname(__file__), JSON_FILE)
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    banner_database = []
    for event in EVENTS_REGISTRY:
        dates = calculate_14_day_cycle(event["start_date"], event["end_date"])
        print(f"\nProcessing {event['event_name']}")
        
        target_vector = get_vibe_vector(event["visual_query"])
        
        scored_products = []
        for item in catalog:
            image_vector = item.get("image_vector")
            if not image_vector:
                continue
            
            sim = normalize_cosine_score(cosine_similarity(target_vector, image_vector))
            scored_products.append({
                "product_id": str(item["id"]),
                "brand": item.get("brand", ""),
                "name": item.get("name", ""),
                "price": item.get("price", 1499.0),
                "image_url": item.get("image_url", ""),
                "score_pct": round(sim * 100, 2)
            })
            
        scored_products.sort(key=lambda x: x["score_pct"], reverse=True)
        top_outfits = scored_products[:15]
        
        event_record = {
            "event_id": event["event_id"],
            "event_name": event["event_name"],
            "event_type": event["event_type"],
            "pincode": event["pincode"],
            "region": event["region"],
            "start_date": event["start_date"],
            "end_date": event["end_date"],
            "duration_days": dates["duration_days"],
            "pre_event_days": dates["pre_event_days"],
            "banner_visibility_start": dates["banner_visibility_start"],
            "banner_visibility_end": dates["banner_visibility_end"],
            "banner_title": event["banner_title"],
            "banner_subtitle": event["banner_subtitle"],
            "banner_theme_color": event["banner_theme_color"],
            "visual_query": event["visual_query"],
            "top_matching_outfits": top_outfits
        }
        banner_database.append(event_record)
        print(f"Attached top {len(top_outfits)} matched outfits (Max score: {top_outfits[0]['score_pct']}%)")

    backend_db_path = os.path.join(os.path.dirname(__file__), "festival_banner_db.json")
    with open(backend_db_path, "w", encoding="utf-8") as f:
        json.dump(banner_database, f, indent=4)
    print("Done!")

if __name__ == "__main__":
    run_banner_engine()
