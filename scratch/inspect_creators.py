import json

with open("backend/pinpulse_mock_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

for pincode in ["800008", "682001", "752001"]:
    creators = [r for r in db if r.get("pincode") == pincode and r.get("type") == "creator"]
    vids = set(r.get("video_id") for r in creators)
    print(f"\n--- PINCODE {pincode} ---")
    print(f"Total creator records: {len(creators)}")
    print(f"Unique video IDs: {vids}")
    for vid in vids:
        recs = [r for r in creators if r.get("video_id") == vid]
        print(f"  Video ID: {vid} (Records: {len(recs)})")

with open("backend/app/youtube_scraper.py", "r", encoding="utf-8") as f:
    code = f.read()

import re
print("\n--- ZIP_CREATOR_VIDEOS channels ---")
channels = re.findall(r'"channel":\s*"([^"]+)"', code)
print(set(channels))
