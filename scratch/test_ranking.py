import sys
import os
import json

sys.path.insert(0, os.path.abspath('backend/app'))
sys.path.insert(0, os.path.abspath('backend'))

from pinpulse_engine import PinPulseEngine
from config import CONTEXT_MATRICES
from main import get_vibe_vector, FESTIVAL_RULES, WEATHER_RULES

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog products in local_catalog.json: {len(catalog)}")

# Modify copy of catalog to ensure zip_codes doesn't filter out products when evaluating full 132 product catalog rank
catalog_all = [p.copy() for p in catalog]
for p in catalog_all:
    p['zip_codes'] = [] # disable regional exclusion for global catalog ranking

engine = PinPulseEngine(
    product_catalog=catalog_all,
    zip_data={
        '800008': {'city': 'Patna', 'state': 'Bihar', 'weather_conditions': 'hot_humid', 'aov': 1800},
        '682001': {'city': 'Kochi', 'state': 'Kerala', 'weather_conditions': 'hot_humid', 'aov': 2200},
        '752001': {'city': 'Puri', 'state': 'Odisha', 'weather_conditions': 'warm_moderate', 'aov': 1500},
        '793001': {'city': 'Shillong', 'state': 'Meghalaya', 'weather_conditions': 'cold', 'aov': 2100},
        '302001': {'city': 'Jaipur', 'state': 'Rajasthan', 'weather_conditions': 'hot_dry', 'aov': 2400},
    },
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

scored_items = engine.score_all_products(user_ctx)
print(f"Total ranked products evaluated: {len(scored_items)}")

# Get last 30
last_30 = scored_items[-30:]

print("\n" + "="*80)
print(f"LAST 30 RANKING OUTFITS (Ranks {len(scored_items)-29} to {len(scored_items)})")
print("="*80)

results_data = []

for idx, item in enumerate(last_30, len(scored_items) - 29):
    info = {
        "rank": idx,
        "id": item.get("id"),
        "name": item.get("name"),
        "category": item.get("category"),
        "price": item.get("price"),
        "final_score": item.get("final_score"),
        "s_aesthetic": item.get("s_aesthetic"),
        "s_fabric": item.get("s_fabric"),
        "s_age": item.get("s_age"),
        "s_price": item.get("s_price"),
        "s_festivity": item.get("s_festivity"),
        "s_boutique": item.get("s_boutique"),
        "s_creator": item.get("s_creator"),
        "s_velocity": item.get("s_velocity"),
        "reasons": []
    }
    # Why low rank?
    reasons = []
    if item.get("s_fabric", 1.0) <= 0.1:
        reasons.append("Severe Weather/Fabric Mismatch (e.g. heavy wool/velvet in hot humid weather)")
    if item.get("s_age", 1.0) <= 0.1:
        reasons.append("Age Demographic Mismatch")
    if item.get("s_price", 1.0) <= 0.2:
        reasons.append("Price Way Above Regional AOV")
    if item.get("s_aesthetic", 1.0) < 0.4:
        reasons.append("Low Aesthetic CLIP Vector Match to User Vibe")
    info["reasons"] = reasons
    results_data.append(info)
    
    print(f"Rank {idx:3d} | ID {item.get('id'):3} | {item.get('name')[:35]:35} | Score: {item.get('final_score'):.3f} | Rs.{item.get('price')} | Cat: {item.get('category')} | Fabric: {item.get('s_fabric')} | Age: {item.get('s_age')} | PriceScore: {item.get('s_price')}")
    if reasons:
        print(f"          Penalties: {', '.join(reasons)}")

with open('scratch/last_30_results.json', 'w', encoding='utf-8') as out_f:
    json.dump(results_data, out_f, indent=2)

print("\nSaved detailed JSON to scratch/last_30_results.json")
