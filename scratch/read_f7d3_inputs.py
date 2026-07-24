import json
import os

tpath = r'C:\Users\HP\.gemini\antigravity-ide\brain\f7d39dc8-0768-4630-ac51-1f89a3637147\.system_generated\logs\transcript.jsonl'

print("=== User Requests in Previous Session (f7d39dc8) ===")

if os.path.exists(tpath):
    with open(tpath, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            try:
                data = json.loads(line)
                if data.get('type') == 'USER_INPUT':
                    text = str(data.get('content', '')).strip()
                    clean = text.replace('<USER_REQUEST>', '').replace('</USER_REQUEST>', '').strip()
                    if clean and not clean.startswith('<ADDITIONAL_METADATA>'):
                        print(f"\n[Step {idx}] USER: {clean[:200]}")
            except:
                pass
