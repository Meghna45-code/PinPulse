import json
import os
import sys

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from main import get_vibe_vector, FALLBACK_CREATORS, FALLBACK_STORES
from scoring_engine import cosine_similarity, normalize_cosine_score

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Find all boots in catalog
boots_items = []
for p in catalog:
    name_lower = p.get('name', '').lower()
    cat_lower = p.get('category', '').lower()
    tags_lower = [t.lower() for t in p.get('tags', [])]
    if 'boot' in name_lower or 'boot' in cat_lower or any('boot' in t for t in tags_lower):
        boots_items.append(p)

print(f"Found {len(boots_items)} boots items in local_catalog.json:")

# 1. Patna Creator & Boutique baseline vector
patna_creators = FALLBACK_CREATORS.get("800008", [])
patna_stores = FALLBACK_STORES.get("800008", [])
patna_vectors = [c['vector'] for c in patna_creators] + [s['vector'] for s in patna_stores]
import numpy as np
patna_trend_vector = np.mean(patna_vectors, axis=0).tolist()

# Rank full catalog against Patna trend vector
patna_ranked = []
for p in catalog:
    img_vec = p.get("image_vector") or p.get("vector") or p.get("embedding")
    raw_cos = cosine_similarity(patna_trend_vector, img_vec) if img_vec else 0.0
    norm_match_pct = round(normalize_cosine_score(raw_cos) * 100, 2)
    patna_ranked.append({"id": p.get("id"), "name": p.get("name"), "score": norm_match_pct, "raw_cos": raw_cos})

# Sort descending (Rank 1 = 100% highest match, Rank 132 = lowest match)
patna_ranked_desc = sorted(patna_ranked, key=lambda x: x["score"], reverse=True)
patna_ranked_asc = sorted(patna_ranked, key=lambda x: x["score"])

# Find rank of boots items
print("\n=== BOOTS RANKING IN PATNA CREATOR & BOUTIQUE TREND FEED ===")
for b in boots_items:
    pid = b.get('id')
    # Rank descending (Top 1 to 132)
    rank_desc = next((i for i, x in enumerate(patna_ranked_desc, 1) if x["id"] == pid), None)
    # Rank ascending (Lowest 1 to 132)
    rank_asc = next((i for i, x in enumerate(patna_ranked_asc, 1) if x["id"] == pid), None)
    score_info = next((x for x in patna_ranked_desc if x["id"] == pid), {})
    print(f"Item ID {pid}: {b.get('name')}")
    print(f"  Category: {b.get('category')} | Price: Rs.{b.get('price')}")
    print(f"  Patna Visual Match Score: {score_info.get('score')}% (Raw Cosine: {score_info.get('raw_cos'):.4f})")
    print(f"  Rank (Descending / Highest Match): Rank #{rank_desc} out of 132")
    print(f"  Rank (Ascending / Bottom List): Rank #{rank_asc} out of 132 (i.e. Rank #{133 - rank_asc} from top)")

# Also check full PinPulse 5-pillar engine rank
from pinpulse_engine import PinPulseEngine
from main import FESTIVAL_RULES, WEATHER_RULES

engine = PinPulseEngine(
    product_catalog=[p.copy() for p in catalog],
    zip_data={'800008': {'city': 'Patna', 'state': 'Bihar', 'weather_conditions': 'hot_humid', 'aov': 1800}},
    festival_rules=FESTIVAL_RULES,
    weather_rules=WEATHER_RULES,
    creators={},
    stores={},
    cf_lookup={}
)

user_ctx = {
    'zip_code': '800008',
    'aesthetic': 'casual',
    'aesthetic_vector': get_vibe_vector('casual'),
    'age_group': 'gen-z',
    'state': 'discovery',
    'session_cart': [],
    'interactions': [],
    'time_offset_hours': 0,
    'date': '2026-08-15'
}

for p in engine.product_catalog:
    p['zip_codes'] = []

scored_all = engine.score_all_products(user_ctx)
print("\n=== BOOTS RANKING IN FULL 5-PILLAR PINPULSE ENGINE ===")
for b in boots_items:
    pid = b.get('id')
    rank = next((i for i, x in enumerate(scored_all, 1) if x.get('id') == pid), None)
    item_scored = next((x for x in scored_all if x.get('id') == pid), {})
    print(f"Item ID {pid}: {b.get('name')}")
    print(f"  Full PinPulse Score: {item_scored.get('final_score')}")
    print(f"  Rank in 132 catalog: Rank #{rank} out of 132")
