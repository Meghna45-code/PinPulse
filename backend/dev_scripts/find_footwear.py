import json

with open('local_catalog.json','r') as f:
    cat = json.load(f)

# Find anything boot/sandal/heel/shoe-like
keywords = ['boot', 'sandal', 'heel', 'shoe', 'slipper', 'footwear', 'mojari', 'juttis']
results = []
for p in cat:
    name_lower = p.get('name', '').lower()
    desc_lower = p.get('description', '').lower()
    tags = p.get('tags', [])
    tags_lower = [t.lower() for t in tags]
    
    if any(kw in name_lower or kw in desc_lower or kw in tags_lower for kw in keywords):
        results.append(p)
        
print(f"Found {len(results)} footwear-like products:")
for p in results:
    print(f"  ID={p['id']} {p['name'][:50]} - tags: {p['tags'][:5]}")
