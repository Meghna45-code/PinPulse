import requests, json

BASE = "http://127.0.0.1:8000"

# Test look completer
r = requests.get(f"{BASE}/api/look-completer", params={"product_id": 1, "occasion_tag": "wedding_day"})
data = r.json()
print("Look Completer (product 1, wedding_day):")
acc = data.get('accessory')
foot = data.get('footwear')
print(f"  Accessory: {acc}")
print(f"  Footwear: {foot}")

# Test with a product that has local fallback
r = requests.get(f"{BASE}/api/look-completer", params={"product_id": 9, "occasion_tag": "festival"})
data = r.json()
print("\nLook Completer (product 9, festival):")
acc = data.get('accessory')
foot = data.get('footwear')
print(f"  Accessory: {acc}")
print(f"  Footwear: {foot}")
