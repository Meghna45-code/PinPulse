import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = f"{os.getenv('SUPABASE_URL')}/rest/v1/"
headers = {
    "apikey": os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}"
}
r = requests.get(url, headers=headers)
spec = r.json()
print("All available tables/definitions:")
for k in spec.get("definitions", {}).keys():
    print("  Table definition:", k)
