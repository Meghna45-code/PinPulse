import os

files_to_check = [
    r"backend/app/main.py",
    r"backend/app/pinpulse_engine.py",
    r"backend/app/scoring_engine.py",
    r"database/schema.sql",
    r"frontend/src/App.jsx",
    r"frontend/src/App.css",
    r"backend/dev_scripts/count_db_rows.py"
]

results = []
for f_path in files_to_check:
    abs_path = os.path.abspath(f_path)
    if os.path.exists(abs_path):
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if "inventory" in line_lower or "stock" in line_lower:
                results.append(f"{f_path}:{idx+1}: {line.strip()}\n")

output_path = r"backend/dev_scripts/inventory_matches.txt"
with open(output_path, "w", encoding="utf-8") as f_out:
    f_out.writelines(results)

print(f"Written inventory matches to {output_path}")
