import os
import json

tpath = r'C:\Users\HP\.gemini\antigravity-ide\brain\c1bd556a-8a70-484a-830c-8a2779be8fb0\.system_generated\logs\transcript.jsonl'

print("=== All User Inputs in Current Conversation (c1bd556a) ===")

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
