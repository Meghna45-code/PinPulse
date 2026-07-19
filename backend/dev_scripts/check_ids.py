import json

with open('local_catalog.json','r') as f:
    cat = json.load(f)

# Check IDs used in LOCAL_OUTFIT_COMPLETER
target_ids = [286, 334, 292, 38, 307]
print("Checking for accessory/footwear IDs in catalog:")
for pid in target_ids:
    matches = [p for p in cat if p.get('id') == pid]
    if matches:
        p = matches[0]
        print(f"  ID={pid}: {p.get('name','')[:50]} - tags: {p.get('tags',[])[:4]}")
    else:
        print(f"  ID={pid}: NOT FOUND")
        
# Show max and min IDs
ids = [p.get('id') for p in cat]
print(f"\nID range in catalog: {min(ids)} - {max(ids)}")
print(f"Total products: {len(cat)}")
