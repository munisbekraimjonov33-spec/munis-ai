import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import asyncio
import random
from openai import OpenAI
from loader import OPENAI_API_KEY

# Determine which provider to use
USE_GEMINI = OPENAI_API_KEY.startswith("AIza")
USE_OPENROUTER = OPENAI_API_KEY.startswith("sk-or-")

if USE_GEMINI:
    genai.configure(api_key=OPENAI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
elif USE_OPENROUTER:
    # OpenRouter configuration
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )
else:
    # Standard OpenAI configuration
    client = OpenAI(api_key=OPENAI_API_KEY)

# List of fallback models for OpenRouter free tier
# We include many to ensure at least one is likely available
OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "xiaomi/mimo-v2-flash:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "google/gemma-3-27b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    "deepseek/deepseek-chat:free",
    "qwen/qwen-2-7b-instruct:free",
    "google/gemma-7b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "gryphe/mythomax-l2-13b:free",
    "open-orca/mistral-7b-openorca:free",
    "undi95/toppy-m-7b:free"
]

async def get_ai_response(text: str) -> str:
    if USE_GEMINI:
        try:
            prompt = (
                "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. "
                "Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. "
                f"Savolga o'zbek tilida javob ber.\n\nFoydalanuvchi: {text}"
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Xatolik (Gemini): {str(e)}"
    
    elif USE_OPENROUTER:
        # Shuffle models to distribute load and avoid hitting the same rate-limited model repeatedly
        available_models = list(OPENROUTER_MODELS)
        random.shuffle(available_models)
        
        # Priority: Try Gemini 2.0 first if it's not and we want quality, 
        # but here we prioritize success, so shuffle is fine.
        
        for model_name in available_models:
            for attempt in range(2): # Try each model 2 times
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. Savolga o'zbek tilida javob ber."},
                            {"role": "user", "content": text}
                        ],
                        timeout=50 # Sufficient timeout for slow free models
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        # Rate limited
                        if attempt == 0:
                            await asyncio.sleep(2) # Short wait before retry
                            continue
                        else:
                            # Try next model
                            break
                    elif "503" in error_msg or "500" in error_msg:
                        # Server error, try next model
                        break
                    else:
                        # Other error, try next model
                        print(f"Error with {model_name}: {error_msg}")
                        break
        
        return "Bot hozirda juda yuqori yuklama ostida. Iltimos, 10-15 soniya kuting va qayta yozing. Men albatta javob beraman! ✨"

    else:
        # Standard OpenAI Call
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. Savolga o'zbek tilida javob ber."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik (OpenAI): {str(e)}"


