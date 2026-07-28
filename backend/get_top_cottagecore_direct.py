import json

with open("real_local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Cottagecore Aesthetic tags & keywords
cottagecore_keywords = [
    "floral", "midi dress", "maxi dress", "tiered", "lace", "crochet", 
    "puff sleeve", "cardigan", "linen", "ditsy", "sage", "lavender", 
    "prairie", "peasant", "ruffle", "printed maxi", "a-line dress"
]

scored_dresses = []
for p in catalog:
    name = str(p.get("name", "")).lower()
    cat = str(p.get("category", "")).lower()
    desc = str(p.get("description", "")).lower()
    tags = [str(t).lower() for t in p.get("tags", []) if t]
    
    # Filter for dresses/skirts
    if not any(k in name or k in cat for k in ["dress", "maxi", "midi", "gown", "skirt"]):
        continue
    
    combined_text = f"{name} {cat} {desc} {' '.join(tags)}"
    score = sum(1 for kw in cottagecore_keywords if kw in combined_text)
    
    if score > 0:
        scored_dresses.append((score, p))

scored_dresses.sort(key=lambda x: x[0], reverse=True)

print("TOP 5 COTTAGECORE DRESSES FROM MYNTRA CATALOG:")
for rank, (score, p) in enumerate(scored_dresses[:5], 1):
    print(f"\n{rank}. {p.get('name')}")
    print(f"   Category: {p.get('category')}")
    print(f"   Price: Rs. {p.get('price', 'N/A')}")
    print(f"   Score: {score} tag matches")
    print(f"   Product URL: {p.get('product_url', 'https://www.myntra.com')}")
    print(f"   Image URL: {p.get('image_url')}")
