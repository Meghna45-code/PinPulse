import os
import requests
from dotenv import load_dotenv
load_dotenv()

# We can query the OpenAPI spec from Postgrest to see details of /regional_boutique_trends
url = f"{os.getenv('SUPABASE_URL')}/rest/v1/"
headers = {
    "apikey": os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}"
}
r = requests.get(url, headers=headers)
spec = r.json()
print("regional_boutique_trends columns:")
definitions = spec.get("definitions", {})
boutique_def = definitions.get("regional_boutique_trends", {})
properties = boutique_def.get("properties", {})
for col, details in properties.items():
    print(f"  {col}: {details.get('type')} ({details.get('format')})")
