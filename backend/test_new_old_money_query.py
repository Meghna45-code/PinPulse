import json
import numpy as np

with open("real_local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

# User's Precise Old Money Specification
query_keywords = [
    "linen dress", "midi dress", "white dress", "cream dress", "linen shirt", 
    "linen trousers", "wide leg", "trench coat", "turtleneck", "wool trousers", 
    "tennis skirt", "pleated skirt", "polo", "blazer", "tailored", "cashmere"
]

color_keywords = ["cream", "beige", "white", "navy", "olive", "camel", "charcoal", "burgundy"]

exclusion_keywords = [
    "kurta", "kurti", "saree", "anarkali", "dupatta", "ethnic", "lehenga", 
    "kaftan", "palazzo", "animal", "neon", "graphic", "printed top"
]

scored_items = []
for p in catalog:
    name = str(p.get("name", "")).lower()
    cat = str(p.get("category", "")).lower()
    desc = str(p.get("description", "")).lower()
    col = str(p.get("color", "")).lower()
    
    combined = f"{name} {cat} {desc} {col}"
    
    # Exclude non-old-money ethnic / loud print items
    if any(ex in combined for ex in exclusion_keywords):
        continue
        
    score = 0
    # Match key garment types
    for kw in query_keywords:
        if kw in combined:
            score += 2
            
    # Match core color palette
    for col_kw in color_keywords:
        if col_kw in combined:
            score += 1
            
    if score >= 2:
        scored_items.append((score, p))

scored_items.sort(key=lambda x: x[0], reverse=True)

print(f"TOTAL MATCHING OLD MONEY SPEC OUTFITS: {len(scored_items)}")
print("=" * 70)
for rank, (score, p) in enumerate(scored_items[:5], 1):
    print(f"RANK #{rank}")
    print(f"NAME: {p.get('name')}")
    print(f"CATEGORY: {p.get('category')}")
    print(f"COLOR: {p.get('color', 'N/A')}")
    print(f"PRICE: Rs. {p.get('price')}")
    print(f"SCORE: {score} points (Garment + Color Palette Alignment)")
    print(f"PRODUCT URL: {p.get('product_url', 'https://www.myntra.com')}")
    print(f"IMAGE URL: {p.get('image_url')}")
    print("-" * 70)
