import json

log_file = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0\.system_generated\logs\transcript.jsonl'

print("=== Looking for Top Ranked Dresses in Transcript Responses ===")

with open(log_file, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        data = json.loads(line)
        content = str(data.get('content', ''))
        if 'PLANNER_RESPONSE' in data.get('type', '') and 'Rank #2' in content:
            print(f"\n================ STEP {idx} PLANNER RESPONSE ================")
            print(content[:1500].encode('ascii', errors='ignore').decode('ascii'))
