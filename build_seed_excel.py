"""
Build pinpulse_youtube_seed.xlsx from creators.xlsx.
Extracts YouTube video IDs from URLs and maps zip codes to the catalog pincodes.
"""
import pandas as pd
import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
CREATORS_FILE = os.path.join(ROOT, "excel_sheets", "creators.xlsx")
STORES_FILE = os.path.join(ROOT, "excel_sheets", "stores.xlsx")
OUTPUT_FILE = os.path.join(ROOT, "pinpulse_youtube_seed.xlsx")

# Odisha catalog uses 752001, but Excel has 753001 — map it
PINCODE_MAP = {
    "800008": "800008",
    "682001": "682001",
    "753001": "752001",  # Odisha: Excel has Cuttack 753001, catalog has Bhubaneswar 752001
}

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    if not url or str(url) == "nan":
        return None
    url = str(url)
    # youtube.com/shorts/VIDEO_ID
    m = re.search(r"shorts/([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    # youtube.com/watch?v=VIDEO_ID
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    # youtu.be/VIDEO_ID
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    return None

# --- Read creators ---
df_creators = pd.read_excel(CREATORS_FILE)
current_zip = None
rows = []

for _, row in df_creators.iterrows():
    zc = row.get("ZIP CODE")
    if pd.notna(zc):
        current_zip = str(int(float(zc)))

    url = row.get("URL")
    vid = extract_video_id(url)
    creator = row.get("CONTENT CREATER")
    
    if vid and current_zip:
        mapped_pin = PINCODE_MAP.get(current_zip, current_zip)
        rows.append({
            "video_id": vid,
            "pincode": mapped_pin,
            "type": "creator",
            "store_name": str(creator) if pd.notna(creator) else "Unknown"
        })

# --- Read stores (they have no video URLs, but let's note them) ---
df_stores = pd.read_excel(STORES_FILE)
store_names = {}
current_zip = None
for _, row in df_stores.iterrows():
    zc = row.get("ZIP CODE")
    if pd.notna(zc):
        current_zip = str(int(float(zc)))
    store = row.get("STORES/MARKET")
    if pd.notna(store) and current_zip:
        mapped_pin = PINCODE_MAP.get(current_zip, current_zip)
        if mapped_pin not in store_names:
            store_names[mapped_pin] = []
        store_names[mapped_pin].append(str(store))

print(f"\nCreator video IDs extracted: {len(rows)}")
for r in rows:
    print(f"  {r['pincode']} | {r['type']} | {r['video_id']} | {r['store_name']}")

print(f"\nStore names by pincode (no video URLs available):")
for pin, names in store_names.items():
    print(f"  {pin}: {', '.join(names)}")

# --- Write seed Excel ---
df_out = pd.DataFrame(rows)
df_out.to_excel(OUTPUT_FILE, index=False)
print(f"\nSeed Excel written to: {OUTPUT_FILE}")
print(f"Total rows: {len(df_out)}")
