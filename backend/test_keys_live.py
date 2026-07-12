import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_MAPS_API_KEY")

def test_youtube():
    print("=== Testing YouTube API ===")
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "Patna ethnic wear shopping haul",
        "maxResults": 2,
        "type": "video",
        "key": key
    }
    r = requests.get(url, params=params)
    print("YouTube Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Success! Found videos:")
        for item in data.get("items", []):
            print("  - Title:", item["snippet"]["title"])
    else:
        print("Error:", r.text)

def test_maps():
    print("\n=== Testing Google Maps Places API ===")
    # Using Text Search API
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": "boutique in Patna, Bihar",
        "key": key
    }
    r = requests.get(url, params=params)
    print("Maps Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        print("Success! Found stores:")
        for place in data.get("results", [])[:3]:
            print(f"  - Name: {place['name']}, Address: {place.get('formatted_address')}")
    else:
        print("Error:", r.text)

if __name__ == "__main__":
    test_youtube()
    test_maps()
