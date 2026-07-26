import pandas as pd
import json
import numpy as np
import ast
import os

print("Loading embeddings...")
pq_df = pd.read_parquet('../fashion_embeddings_complete.parquet')
pq_df['p_id'] = pq_df['p_id'].astype(str).str.split('.').str[0]

print("Loading CSV metadata...")
csv_df = pd.read_csv('../archive/Fashion Dataset.csv')
csv_df['p_id'] = csv_df['p_id'].astype(str).str.split('.').str[0]

print("Merging...")
merged = pd.merge(csv_df, pq_df, on='p_id', how='inner')

print(f"Merged count: {len(merged)}")

def parse_attributes(attr_str):
    if pd.isna(attr_str):
        return {}
    try:
        return ast.literal_eval(attr_str)
    except:
        return {}

def to_list(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    return list(x)

records = []
for idx, row in merged.iterrows():
    attrs = parse_attributes(row.get('p_attributes', ''))
    # Try to extract a useful category
    category = attrs.get('Top Type', attrs.get('Bottom Type', attrs.get('Print or Pattern Type', 'apparel')))
    nature = attrs.get('Occasion', 'casual')
    
    price = 0
    try:
        price = float(row.get('price', 0))
    except:
        pass

    record = {
        "id": row['p_id'],
        "name": str(row.get('name', '')),
        "description": str(row.get('description', '')),
        "category": category,
        "nature": nature,
        "price": price,
        "color": str(row.get('colour', '')),
        "brand": str(row.get('brand', '')),
        "image_url": str(row.get('img', '')),
        "attributes": attrs,
        "image_vector": to_list(row['image_embeddings']),
        "text_vector": to_list(row['text_embeddings'])
    }
    records.append(record)

out_path = 'real_local_catalog.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(records, f)

print(f"Successfully generated {out_path} with {len(records)} items.")
