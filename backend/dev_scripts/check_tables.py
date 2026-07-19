import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Let's create the tables via SQL query using pg_graphql or Supabase API if possible
# Since we have service role key, we can also use postgres directly if we have an endpoint or execute SQL via postgres connection.
# Let's check what tables are there or if we can run raw sql using postgrest.
# Alternatively, we can check if there are functions to execute raw SQL.
try:
    # Check if we can run a simple RPC or see if the table exists
    res = sb.table('youtube_trends').select('*').limit(1).execute()
    print("youtube_trends table exists!")
except Exception as e:
    print(f"youtube_trends table does not exist or error: {e}")
