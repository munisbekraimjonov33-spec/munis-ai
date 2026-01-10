import google.generativeai as genai
from loader import OPENAI_API_KEYS
import os

print(f"Total API Keys found: {len(OPENAI_API_KEYS)}")

for i, key in enumerate(OPENAI_API_KEYS):
    print(f"\nTesting Key {i+1}: {key[:8]}...")
    genai.configure(api_key=key)
    try:
        models = genai.list_models()
        print("Available models:")
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Error for key {i+1}: {e}")
