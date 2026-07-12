import json

with open('local_catalog.json','r') as f:
    cat = json.load(f)

# Check products with 'festive' tag
festive = [p for p in cat if 'festive' in p.get('tags', [])]
print(f'Festive products: {len(festive)}')
for p in festive[:5]:
    name = p.get('name','')[:50]
    tags = str(p.get('tags',[])[:6])
    pid = p.get('id')
    print(f'  #{pid} {name} | tags: {tags}')
    
# Check embedding existence
with_embed = [p for p in cat if p.get('embedding')]
print(f'\nProducts with embeddings: {len(with_embed)}/{len(cat)}')

# Check winter products
winter = [p for p in cat if 'winter' in p.get('tags', [])]
print(f'Winter products: {len(winter)}')
for p in winter[:3]:
    name = p.get('name','')[:50]
    tags = str(p.get('tags',[])[:6])
    print(f'  {name} | tags: {tags}')
