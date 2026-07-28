import json

with open("real_local_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

old_money_items = [
    p for p in catalog 
    if any(k in (str(p.get("name","")) + " " + str(p.get("category",""))).lower() for k in ["blazer", "trousers", "linen", "suit", "cashmere", "tweed", "turtleneck", "structured", "coat", "shirt"])
    and not any(k in (str(p.get("name","")) + " " + str(p.get("category",""))).lower() for k in ["kurta", "kurti", "saree", "anarkali", "dupatta", "ethnic", "lehenga", "kaftan", "palazzo"])
]

print(f"TOTAL STRICT OLD MONEY WESTERN ITEMS: {len(old_money_items)}")
print("=" * 60)
for rank, p in enumerate(old_money_items[:5], 1):
    print(f"{rank}. NAME: {p.get('name')}")
    print(f"   CATEGORY: {p.get('category')}")
    print(f"   PRICE: Rs. {p.get('price')}")
    print(f"   PRODUCT URL: {p.get('product_url', 'https://www.myntra.com')}")
    print(f"   IMAGE URL: {p.get('image_url')}")
    print("-" * 60)
