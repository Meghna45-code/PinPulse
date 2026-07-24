import json
import os
import sys

sys.path.insert(0, os.path.abspath('backend/app'))

mock_db_file = 'backend/pinpulse_mock_db.json'
if os.path.exists(mock_db_file):
    with open(mock_db_file, 'r', encoding='utf-8') as f:
        mock_data = json.load(f)
    print("Mock DB keys of first record:", list(mock_data[0].keys()) if mock_data else "Empty")
    for r in mock_data[:5]:
        print("Record:", r.get('creator_name') or r.get('channel_title'), "| Video:", r.get('video_title') or r.get('title'), "| Thumbnail:", r.get('thumbnail_url') or r.get('video_screenshot_url') or r.get('thumbnail'))

from main import FALLBACK_CREATORS, FALLBACK_STORES

print("\n--- Patna (800008) Fallback Creators ---")
for c in FALLBACK_CREATORS.get("800008", []):
    print("Creator:", c.get("name"))
    for v in c.get("videos", []):
        print("  Video Title:", v.get("title"))
        print("  Screenshot:", v.get("video_screenshot_url"))

print("\n--- Patna (800008) Fallback Stores ---")
for s in FALLBACK_STORES.get("800008", []):
    print("Store:", s.get("name"), "| Trend Vector:", s.get("extracted_visual_trend"))
