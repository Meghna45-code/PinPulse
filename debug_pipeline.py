"""Debug: test transcript fetch + Gemini for the 8 video IDs."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

VIDEO_IDS = [
    "U_nkHYPc1ww", "FqilEHTE5BA", "55apryEpLEs",  # Patna
    "J_F2dzbUXvg", "mZPnF5dMzcM", "Vh7B2k8-CLc",  # Kochi
    "erCRv3qln1Q", "rmZXaeTxjDg",                   # Odisha
]

print("=== TESTING TRANSCRIPT FETCH ===")
for vid in VIDEO_IDS:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid)
        text = " ".join([e["text"] for e in transcript])
        print(f"  {vid}: OK ({len(text)} chars) — '{text[:80]}...'")
    except Exception as e:
        print(f"  {vid}: FAILED — {e}")

print("\n=== TESTING GEMINI API ===")
key = os.getenv("GEMINI_API_KEY")
print(f"  Key found: {bool(key)}")
if key:
    genai.configure(api_key=key)
    try:
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        resp = model.generate_content("Say hello in one word.")
        print(f"  Gemini response: {resp.text.strip()}")
    except Exception as e:
        print(f"  Gemini FAILED: {e}")
