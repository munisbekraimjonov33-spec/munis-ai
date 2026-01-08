import google.generativeai as genai
from loader import OPENAI_API_KEY
import os

# Configure using the key from loader
genai.configure(api_key=OPENAI_API_KEY)

print(f"API Key starts with: {OPENAI_API_KEY[:4]}...")

print("Available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
