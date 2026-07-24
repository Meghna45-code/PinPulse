import os
import json

target_conv_ids = [
    "c1bd556a-8a70-484a-830c-8a2779be8fb0",
    "f7d39dc8-0768-4630-ac51-1f89a3637147",
    "f89b1a9d-0aa6-439a-b290-63b2fca3367f",
    "d90c5263-da5e-4b94-908c-06837958cf06"
]

brain_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain'

print("=== Reading User Requests from PinPulse Conversations ===")

for cid in target_conv_ids:
    tpath = os.path.join(brain_dir, cid, '.system_generated', 'logs', 'transcript.jsonl')
    if os.path.exists(tpath):
        print(f"\n================ CONVERSATION {cid} ================")
        with open(tpath, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f):
                try:
                    data = json.loads(line)
                    if data.get('type') == 'USER_INPUT':
                        text = str(data.get('content', '')).strip()
                        # Clean tags
                        clean_text = text.replace('<USER_REQUEST>', '').replace('</USER_REQUEST>', '').strip()
                        if clean_text and not clean_text.startswith('<ADDITIONAL_METADATA>'):
                            print(f"[Line {idx}] USER: {clean_text[:150]}")
                except:
                    pass
