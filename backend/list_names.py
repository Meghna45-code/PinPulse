import os
import json

LOCAL_CATALOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "local_catalog.json"))

def list_names():
    if not os.path.exists(LOCAL_CATALOG_FILE):
        print("local_catalog.json not found.")
        return
        
    with open(LOCAL_CATALOG_FILE, "r") as f:
        products = json.load(f)
        
    print(f"--- START OF NAMES (Total: {len(products)}) ---")
    for p in products:
        print(f"{p['id']}: {p['name']}")
    print("--- END OF NAMES ---")

if __name__ == "__main__":
    list_names()
