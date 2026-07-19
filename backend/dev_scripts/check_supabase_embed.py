import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

# Check product count
cnt = sb.table('products').select('id', count='exact').execute()
print(f'Total products in Supabase: {cnt.count}')

# Check first few products and embedding status
res = sb.table('products').select('id, name, tags, embedding').limit(5).execute()
for p in res.data:
    emb = p.get('embedding')
    has_emb = emb is not None and len(str(emb)) > 10
    pid = p['id']
    name = p['name'][:40]
    tags = str(p['tags'][:4])
    print(f'ID={pid} {name} - emb: {"YES" if has_emb else "NO"} - tags: {tags}')

# Count how many have embeddings
all_res = sb.table('products').select('id, embedding').execute()
with_embed = sum(1 for p in all_res.data if p.get('embedding'))
print(f'\nProducts with embeddings: {with_embed}/{cnt.count}')
