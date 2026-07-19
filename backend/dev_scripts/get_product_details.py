import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_product():
    if not SUPABASE_URL:
        print("No Supabase URL")
        return
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        res = supabase.table("products").select("*").ilike("name", "%dhoti%").execute()
        print("Matches for 'dhoti':", res.data)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    get_product()
