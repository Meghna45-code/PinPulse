import os
import glob
import json

brain_dir = r'C:\Users\HP\.gemini\antigravity-ide\brain'

print("=== Checking all conversation folders in brain directory ===")

if os.path.exists(brain_dir):
    subdirs = [d for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d))]
    print("Conversation directories:", subdirs)
    
    for d in subdirs:
        transcript_path = os.path.join(brain_dir, d, '.system_generated', 'logs', 'transcript.jsonl')
        if os.path.exists(transcript_path):
            size_kb = round(os.path.getsize(transcript_path) / 1024, 1)
            print(f"\n--- Conversation ID: {d} (Transcript Size: {size_kb} KB) ---")
            
            # Read user inputs from transcript
            user_inputs = []
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'USER_INPUT':
                            inp_text = str(data.get('content', '')).strip()
                            if inp_text:
                                user_inputs.append(inp_text[:120])
                    except:
                        pass
            print(f"Total User Inputs: {len(user_inputs)}")
            print("First 5 user inputs:")
            for u in user_inputs[:5]:
                print("  -", u)
else:
    print("Brain directory not found!")
