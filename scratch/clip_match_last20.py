import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from main import get_vibe_vector
from scoring_engine import cosine_similarity, normalize_cosine_score

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog length evaluated: {len(catalog)}")

# User aesthetic vector (e.g., 'casual' or 'festive' or baseline visual vibe)
user_aesthetic = "casual"
user_vector = get_vibe_vector(user_aesthetic)

# Rank products purely based on CLIP image_vector cosine similarity against user aesthetic vector
clip_ranked = []
for p in catalog:
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    if img_vec:
        raw_cos = cosine_similarity(user_vector, img_vec)
        # Match percentage = normalized cosine score * 100 or raw similarity * 100
        norm_match_pct = round(normalize_cosine_score(raw_cos) * 100, 2)
        raw_cos_pct = round(raw_cos * 100, 2)
    else:
        norm_match_pct = 0.0
        raw_cos_pct = 0.0
        
    clip_ranked.append({
        "id": p.get("id"),
        "name": p.get("name"),
        "category": p.get("category"),
        "price": p.get("price"),
        "raw_cos": raw_cos,
        "norm_match_pct": norm_match_pct,
        "raw_cos_pct": raw_cos_pct,
        "nature": p.get("nature", ""),
        "tags": p.get("tags", [])
    })

# Sort by normalized match percentage descending (100% highest to 0% lowest)
clip_ranked.sort(key=lambda x: x["norm_match_pct"], reverse=True)

print("\n" + "="*80)
print(f"LAST 20 PURE CLIP FASHION MATCHES (Ranks {len(clip_ranked)-19} to {len(clip_ranked)})")
print("="*80)

last_20 = clip_ranked[-20:]
for idx, item in enumerate(last_20, len(clip_ranked) - 19):
    print(f"Rank {idx:3d} | ID {item['id']:3} | {item['name'][:40]:40} | CLIP Match: {item['norm_match_pct']}% (Raw Cos: {item['raw_cos']:.4f}) | Category: {item['category']}")

with open('scratch/clip_last_20_results.json', 'w', encoding='utf-8') as out_f:
    json.dump(last_20, out_f, indent=2)
