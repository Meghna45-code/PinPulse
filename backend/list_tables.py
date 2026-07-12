import os
import requests
from dotenv import load_dotenv
load_dotenv()

# We can query the OpenAPI spec from Postgrest to see all tables and schemas!
url = f"{os.getenv('SUPABASE_URL')}/rest/v1/"
headers = {
    "apikey": os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}"
}
r = requests.get(url, headers=headers)
if r.status_code == 200:
    spec = r.json()
    print("Tables list:")
    for path in spec.get("paths", {}).keys():
        print("  Path:", path)
else:
    print("Error:", r.status_code, r.text)
