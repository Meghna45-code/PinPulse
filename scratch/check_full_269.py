import json
import os
import glob
import pandas as pd

print("=== Checking catalog files for total 269 products ===")

with open('backend/local_catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)
print(f"local_catalog.json count: {len(cat)}")

if os.path.exists('backend/dev_scripts/large_catalog_checkpoint.json'):
    with open('backend/dev_scripts/large_catalog_checkpoint.json', 'r', encoding='utf-8') as f:
        lcc = json.load(f)
    print(f"large_catalog_checkpoint.json count: {len(lcc)}")

# Check Excel files
total_excel_rows = 0
for x in glob.glob("excel_sheets/*.xlsx"):
    try:
        df = pd.read_excel(x)
        print(f"Excel {x}: {len(df)} rows")
        total_excel_rows += len(df)
    except Exception as e:
        print(f"Excel error {x}: {e}")

# Check generate_large_catalog.py if it exists
gen_script = 'backend/dev_scripts/generate_large_catalog.py'
if os.path.exists(gen_script):
    with open(gen_script, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print("generate_large_catalog.py snippet:")
    for line in lines[:20]:
        print("  ", line.strip())
