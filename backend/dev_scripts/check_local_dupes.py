import os
import json

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))

def check_local():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        print("local_catalog.json not found.")
        return
        
    with open(LOCAL_CATALOG_FILE, "r") as f:
        products = json.load(f)
        
    print(f"Total products in local catalog: {len(products)}")
    seen = {}
    duplicates = []
    for p in products:
        key = (p["name"].strip().lower(), p["description"].strip().lower())
        if key in seen:
            seen[key].append(p.get("id"))
            duplicates.append(p)
        else:
            seen[key] = [p.get("id")]
            
    print(f"Unique product count: {len(seen)}")
    print(f"Duplicate count: {len(duplicates)}")
    if duplicates:
        print("Example duplicates (top 10):")
        for dup in duplicates[:10]:
            key = (dup["name"].strip().lower(), dup["description"].strip().lower())
            print(f" - Name: {dup['name']} | IDs: {seen[key]}")

if __name__ == "__main__":
    check_local()
