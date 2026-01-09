import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import asyncio
import random
import logging
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
    "undi95/toppy-m-7b:free",
    "mistralai/mistral-small-24b-instruct-2501:free",
    "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "liquid/lfm-40b:free"
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
            logging.error(f"Gemini error: {e}")
            return f"Xatolik (Gemini): {str(e)}"
    
    elif USE_OPENROUTER:
        available_models = list(OPENROUTER_MODELS)
        
        # We try the entire list up to 2 times (two passes)
        for pass_num in range(2):
            random.shuffle(available_models)
            for model_name in available_models:
                for attempt in range(1): # Try each model once per pass
                    try:
                        logging.info(f"Trying AI model: {model_name} (Pass {pass_num+1})")
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. Savolga o'zbek tilida javob ber."},
                                {"role": "user", "content": text}
                            ],
                            timeout=40
                        )
                        return response.choices[0].message.content
                    except Exception as e:
                        error_msg = str(e)
                        if "429" in error_msg:
                            logging.warning(f"Model {model_name} rate limited (429)")
                            continue
                        elif "503" in error_msg or "504" in error_msg or "500" in error_msg:
                            logging.warning(f"Model {model_name} server error ({error_msg[:10]}...)")
                            continue
                        else:
                            logging.error(f"Error with {model_name}: {error_msg}")
                            continue
            
            # If all models failed in the first pass, wait a bit before the second pass
            if pass_num == 0:
                logging.info("All models failed in pass 1, waiting 5 seconds before pass 2...")
                await asyncio.sleep(5)
        
        return "Uzr, hozirda barcha bepul AI xizmatlari band bo'lib qoldi. Iltimos, 20-30 soniyadan so'ng qayta urinib ko'ring yoki boshqa savol bering. Men sizga yordam berishni juda xohlayman! ✨"

    else:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Savolga o'zbek tilida javob ber."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik (OpenAI): {str(e)}"


