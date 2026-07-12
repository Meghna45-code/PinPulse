import json

with open('local_catalog.json','r') as f:
    cat = json.load(f)

# Find accessory products
accessories = [p for p in cat if 'accessories' in p.get('tags', [])]
print("=== ACCESSORY PRODUCTS ===")
for p in accessories:
    print(f"  ID={p['id']} {p['name'][:50]} - tags: {p['tags'][:5]}")

# Find footwear products
footwear = [p for p in cat if any(t in p.get('tags', []) for t in ['footwear', 'heels', 'sandals', 'boots', 'shoes'])]
print("\n=== FOOTWEAR PRODUCTS ===")
for p in footwear:
    print(f"  ID={p['id']} {p['name'][:50]} - tags: {p['tags'][:5]}")

# Find necklace/jewelry
jewelry = [p for p in cat if any(t in p.get('tags', []) for t in ['necklace', 'jewelry', 'earrings', 'anklet', 'kundan'])]
print("\n=== JEWELRY/NECKLACE PRODUCTS ===")
for p in jewelry:
    print(f"  ID={p['id']} {p['name'][:50]} - tags: {p['tags'][:5]}")
