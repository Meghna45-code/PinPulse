"""Validate the generated pinpulse_mock_db.json."""
import json, os
db_path = os.path.join(os.path.dirname(__file__), "backend", "pinpulse_mock_db.json")
with open(db_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
pincodes = {}
types = {}
for r in data:
    p = r["pincode"]
    t = r["type"]
    pincodes[p] = pincodes.get(p, 0) + 1
    types[t] = types.get(t, 0) + 1

print(f"\nRecords by pincode:")
for p, c in sorted(pincodes.items()):
    print(f"  {p}: {c} records")

print(f"\nRecords by type:")
for t, c in sorted(types.items()):
    print(f"  {t}: {c} records")

# Check vector dimensions
vec_lens = set()
for r in data:
    vec_lens.add(len(r.get("vector", [])))
print(f"\nVector dimensions: {vec_lens}")

# Check catalog matches
matched = sum(1 for r in data if r.get("matched_product_id") is not None)
print(f"Catalog matches: {matched}/{len(data)}")

# Show sample items per pincode
print(f"\n=== SAMPLE ITEMS ===")
seen = set()
for r in data:
    p = r["pincode"]
    if p not in seen:
        seen.add(p)
        meta = r["metadata"]
        print(f"\n  [{p}] {meta.get('item', '?')}")
        print(f"    Description: {meta.get('description', '?')[:80]}...")
        print(f"    Tags: {meta.get('tags', [])}")
        print(f"    Matched to: {r.get('matched_product_name', '?')} (score={r.get('hybrid_score', 0):.4f})")
