"""
Fix the outfit_completer table in Supabase to use valid product IDs (1-159).
The old data had IDs 286, 292, 307, 334 which don't exist in the products table.
New correct mappings:
  - ID=124: Heavy kundan necklace set  (was 286)
  - ID=127: Traditional silver anklets  (was 292)
  - ID=135: Minimalist gold earring set (was 307)
  - ID=149: Modern ankle boots for women (was 334)
  - ID=38:  Wangala Tribal Beaded Vest (unchanged)
"""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Check if outfit_completer table exists and has data
try:
    res = sb.table('outfit_completer').select('*').execute()
    print(f"Current outfit_completer rows: {len(res.data)}")
    for row in res.data:
        print(f"  {row}")
except Exception as e:
    print(f"Error querying outfit_completer: {e}")
    exit(1)

# Delete all existing rows
try:
    sb.table('outfit_completer').delete().neq('primary_item_id', -999).execute()
    print("\nDeleted all existing rows")
except Exception as e:
    print(f"Error deleting: {e}")
    exit(1)

# Insert correct mappings
correct_mappings = [
    {"primary_item_id": 1,   "occasion_tag": "wedding_day", "suggested_accessory_id": 124, "suggested_footwear_id": 149},
    {"primary_item_id": 2,   "occasion_tag": "wedding_day", "suggested_accessory_id": 124, "suggested_footwear_id": 149},
    {"primary_item_id": 9,   "occasion_tag": "festival",    "suggested_accessory_id": 127, "suggested_footwear_id": 149},
    {"primary_item_id": 7,   "occasion_tag": "festival",    "suggested_accessory_id": 127, "suggested_footwear_id": None},
    {"primary_item_id": 16,  "occasion_tag": "festival",    "suggested_accessory_id": 127, "suggested_footwear_id": None},
    {"primary_item_id": 97,  "occasion_tag": "wedding_day", "suggested_accessory_id": 124, "suggested_footwear_id": 149},
    {"primary_item_id": 110, "occasion_tag": "festival",    "suggested_accessory_id": 38,  "suggested_footwear_id": 149},
    {"primary_item_id": 112, "occasion_tag": "festival",    "suggested_accessory_id": 135, "suggested_footwear_id": 149},
    {"primary_item_id": 6,   "occasion_tag": "wedding_day", "suggested_accessory_id": 124, "suggested_footwear_id": 149},
    {"primary_item_id": 5,   "occasion_tag": "festival",    "suggested_accessory_id": 156, "suggested_footwear_id": 149},
    {"primary_item_id": 17,  "occasion_tag": "festival",    "suggested_accessory_id": 127, "suggested_footwear_id": None},
]

try:
    res = sb.table('outfit_completer').insert(correct_mappings).execute()
    print(f"Inserted {len(correct_mappings)} new rows successfully!")
    
    # Verify
    verify = sb.table('outfit_completer').select('*').execute()
    print(f"\nVerification - Total rows now: {len(verify.data)}")
    for row in verify.data:
        print(f"  product={row.get('primary_item_id')} occasion={row.get('occasion_tag')} -> acc={row.get('suggested_accessory_id')} foot={row.get('suggested_footwear_id')}")
except Exception as e:
    print(f"Error inserting: {e}")
