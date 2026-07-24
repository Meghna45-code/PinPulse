"""
Restore the full 157-product catalog from Supabase, then inject
the CLIP image_vector and vibe embedding into products 1-60.
"""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
LOCAL_CATALOG_FILE = os.path.join(os.path.dirname(__file__), "local_catalog.json")

print("Fetching full product catalog from Supabase...")
from supabase import create_client
sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
res = sb.table("products").select("*").execute()
products = res.data
print(f"Fetched {len(products)} products from Supabase")

# Save locally
with open(LOCAL_CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(products, f, indent=4)
print(f"Saved {len(products)} products to {LOCAL_CATALOG_FILE}")
