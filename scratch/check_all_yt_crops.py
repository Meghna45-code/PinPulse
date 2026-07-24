import json
import pandas as pd
import os

# Check youtube_metadata_cache.json
with open('backend/youtube_metadata_cache.json', 'r', encoding='utf-8', errors='ignore') as f:
    ym = json.load(f)

print("=== youtube_metadata_cache.json - ALL ENTRIES ===")
for vid, data in ym.items():
    title = data.get('title', '')[:60]
    print(f"  VideoID: {vid} | Title: {title}")

# Check pinpulse_youtube_seed.xlsx for ALL Patna (800008) creators
df = pd.read_excel('pinpulse_youtube_seed.xlsx')
patna_entries = df[df['pincode'] == 800008]
print(f"\n=== ALL PATNA (800008) creators in pinpulse_youtube_seed.xlsx ===")
print(patna_entries.to_string())

# Check creators.xlsx for all Patna creators
df_c = pd.read_excel('excel_sheets/creators.xlsx')
print(f"\n=== All creators in excel_sheets/creators.xlsx ===")
print(df_c.to_string())

# Check what yolo crop thumbnails exist in artifacts
artifacts_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0'
all_yt_crops = [f for f in os.listdir(artifacts_dir) if 'yt_crop' in f or 'thumb' in f.lower()]
print(f"\n=== All YT crop / thumbnail files in artifacts dir ===")
for f in sorted(all_yt_crops):
    print(f"  {f}")
