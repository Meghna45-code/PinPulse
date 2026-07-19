import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
res = sb.table('regional_boutique_trends').select('*').execute()
print(f'Total rows in DB: {len(res.data)}')
for row in res.data:
    print(f"  {row.get('store_id')}: {row.get('store_name')} ({row.get('social_signal_source')}) - Trend: {row.get('extracted_visual_trend')}")
