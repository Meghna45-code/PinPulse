import requests, json

BASE = "http://127.0.0.1:8000"

def test_all():
    # 1. System state
    r = requests.get(f"{BASE}/api/system-state")
    print("=== System State ===")
    print(json.dumps(r.json(), indent=2))
    
    # 2. Products for Patna - Chhath Puja (festive)
    r = requests.get(f"{BASE}/api/products", params={
        "zip_code": "800001", "date": "2026-11-15", "vibe": "festive"
    })
    data = r.json()
    print(f"\n=== Products (Patna, Chhath Puja, festive vibe) ===")
    print(f"Total: {len(data)}")
    for p in data[:5]:
        print(f"  #{p['id']} {p['name']} -> {p['final_score']:.4f} | trending: {p['is_trending']}")
    
    # 3. Products for Bengaluru - Streetwear
    r = requests.get(f"{BASE}/api/products", params={
        "zip_code": "560034", "date": "2026-11-15", "vibe": "streetwear"
    })
    data = r.json()
    print(f"\n=== Products (Bengaluru, streetwear vibe) ===")
    print(f"Total: {len(data)}")
    for p in data[:5]:
        print(f"  #{p['id']} {p['name']} -> {p['final_score']:.4f}")

    # 4. Boutiques  
    r = requests.get(f"{BASE}/api/trends/boutiques", params={"zip_code": "560034"})
    data = r.json()
    print(f"\n=== Boutiques (Bengaluru) ===")
    for b in data.get('boutiques', [])[:3]:
        print(f"  {b['store_name']} ({b['locality']}) - {b['extracted_visual_trend']} - rating: {b['rating']}")
    
    # 5. YouTube trends
    r = requests.get(f"{BASE}/api/trends/youtube", params={"zip_code": "800001"})
    data = r.json()
    print(f"\n=== YouTube Trends (Patna) ===")
    print(f"Total: {len(data)}")
    for item in data[:3]:
        vid = item['youtube_video']
        match = item['matched_product']
        match_name = match['name'] if match else 'No match'
        print(f"  Video: {vid['title'][:50]}... -> Match: {match_name[:40]}")

if __name__ == "__main__":
    test_all()
