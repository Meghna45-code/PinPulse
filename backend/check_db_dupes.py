import os
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def check_dupes():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("Supabase credentials missing.")
        return
        
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Fetch all products
        res = supabase.table("products").select("id, name, description").execute()
        products = res.data
        print(f"Total products in Supabase: {len(products)}")
        
        # Group by name/description
        seen = {}
        duplicates = []
        for p in products:
            key = (p["name"].strip().lower(), p["description"].strip().lower())
            if key in seen:
                seen[key].append(p["id"])
                duplicates.append(p)
            else:
                seen[key] = [p["id"]]
                
        print(f"Unique product count: {len(seen)}")
        print(f"Duplicate count: {len(duplicates)}")
        if duplicates:
            print("Example duplicates (top 5):")
            for dup in duplicates[:5]:
                key = (dup["name"].strip().lower(), dup["description"].strip().lower())
                print(f" - Name: {dup['name']} | IDs: {seen[key]}")
                
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_dupes()
