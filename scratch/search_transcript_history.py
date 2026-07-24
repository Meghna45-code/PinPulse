import json
import os

log_file = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0\.system_generated\logs\transcript.jsonl'

print("=== Searching Transcript for Agreed-Upon Algorithm and 2nd Position Dress ===")

if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                content = str(data.get('content', ''))
                # Search for keywords like "2nd position", "Rank #2", "table", "Patna", "matching"
                if any(k in content.lower() for k in ["2nd", "rank #2", "second position", "agreed", "matching percentage", "saree", "kurta"]):
                    print(f"\n--- Line {idx} ({data.get('type')}) ---")
                    # Print snippet of content
                    snippet = content[:500].replace('\n', ' ')
                    print(snippet)
            except Exception as e:
                pass
else:
    print("Transcript log file not found!")
