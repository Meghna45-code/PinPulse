import json

with open('pinpulse_mock_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print(f'Total records: {len(db)}')
print()
for r in db:
    print(f'  [{r["pincode"]}] {r["video_id"]} -> "{r["matched_product_name"]}"')
    print(f'         item: {r["metadata"]["item"]}')
    print(f'         rrf={r["rrf_score"]}  sources={r["query_sources"]}')
    print()
