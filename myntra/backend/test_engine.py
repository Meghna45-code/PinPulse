"""Quick verification that the PinPulse engine runs end-to-end."""
import sys
sys.path.insert(0, '../data')

from pinpulse_engine import PinPulseEngine
from mock_catalog import PRODUCT_CATALOG
from mock_zip_data import ZIP_DATA, FESTIVAL_RULES, WEATHER_RULES, CREATORS, STORES, CF_LOOKUP

# Initialize engine
engine = PinPulseEngine(
    product_catalog=PRODUCT_CATALOG,
    zip_data=ZIP_DATA,
    festival_rules=FESTIVAL_RULES,
    weather_rules=WEATHER_RULES,
    creators=CREATORS,
    stores=STORES,
    cf_lookup=CF_LOOKUP,
)

# Test with Patna user context
user_context = {
    "zip_code": "800008",
    "aesthetic": "ethnic",
    "aesthetic_vector": PRODUCT_CATALOG[0]["aesthetic_vector"],
    "age_group": "gen-z",
    "state": "discovery",
    "session_cart": [],
    "interactions": [],
    "time_offset_hours": 0,
}

# Score all products
results = engine.score_all_products(user_context)

print(f"Scored {len(results)} products (after veto)")
print("\nTop 5 Recommendations:")
print("-" * 60)
for i, item in enumerate(results[:5]):
    print(f"{i+1}. {item['name']}")
    print(f"   Score: {item['final_score']:.3f} | Cat: {item['category']}")
    print(f"   A:{item['s_aesthetic']:.2f} F:{item['s_fabric']:.2f} Fe:{item['s_festivity']:.2f} C:{item['s_creator']:.2f} B:{item['s_boutique']:.2f}")
    if item.get('reason_labels'):
        print(f"   Labels: {item['reason_labels']}")
    print()

# Test PDP recommendations
print("\nPDP Shelf for prod_001:")
pdp = engine.get_pdp_recommendations("prod_001")
for item in pdp:
    print(f"  - {item['name']} (₹{item['price']})")

# Test velocity surge
print("\nVelocity Surge (Patna):")
surge = engine.simulate_velocity_surge("800008")
print(f"  Theme: {surge['theme']}")
print(f"  Log: {surge['log']}")

print("\n✅ All systems operational!")
