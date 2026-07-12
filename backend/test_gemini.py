import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Check keys
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
print("GEMINI_API_KEY exists in env:", gemini_key is not None)

if gemini_key:
    genai.configure(api_key=gemini_key)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello! What model are you?")
        print("Success:", response.text)
    except Exception as e:
        print("Error calling Gemini API:", e)
else:
    print("No Gemini API key available in env.")
