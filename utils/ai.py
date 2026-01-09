import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import asyncio
import random
import logging
import os
from openai import AsyncOpenAI
from loader import OPENAI_API_KEY

# Determine which provider to use
USE_GEMINI = OPENAI_API_KEY.startswith("AIza")
USE_OPENROUTER = OPENAI_API_KEY.startswith("sk-or-")

if USE_GEMINI:
    genai.configure(api_key=OPENAI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
elif USE_OPENROUTER:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENAI_API_KEY,
    )
else:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Expanded list of fallback models for OpenRouter free tier
OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemini-flash-1.5-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "xiaomi/mimo-v2-flash:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "google/gemma-2-9b-it:free",
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
    "liquid/lfm-40b:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "sophosympatheia/rogue-rose-103b-v0.2:free"
]

async def get_ai_response(text: str) -> str:
    if USE_GEMINI:
        try:
            prompt = (
                "Sen 'Munis AI' ismli yordamchisan. Savolga o'zbek tilida javob ber.\n"
                f"Foydalanuvchi: {text}"
            )
            # Use run_in_executor for the synchronous genai call to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            return response.text
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return f"Xatolik (Gemini): API kalitingizni yoki limitlarni tekshiring. Xato: {str(e)[:50]}..."
    
    elif USE_OPENROUTER:
        available_models = list(OPENROUTER_MODELS)
        last_error = ""
        
        # We try up to 3 passes for extreme cases
        for pass_num in range(3):
            random.shuffle(available_models)
            for model_name in available_models:
                try:
                    logging.info(f"Trying AI model: {model_name} (Pass {pass_num+1})")
                    response = await client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Savolga o'zbek tilida javob ber."},
                            {"role": "user", "content": text}
                        ],
                        timeout=45
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    last_error = str(e)
                    if "401" in last_error or "Authentication" in last_error:
                        return "Xatolik: API kalitingiz noto'g'ri yoki bloklangan. Iltimos, Render sozlamalarida OPENAI_API_KEY ni yangilang."
                    
                    logging.warning(f"Model {model_name} failed: {last_error[:50]}...")
                    continue
            
            # Between passes, wait a bit
            await asyncio.sleep(3)
        
        return (
            "Hozirda barcha bepul AI modellari band. 😔\n\n"
            "**Sabab:** OpenRouter bepul modellari serverlari hozirda juda katta yuklama ostida.\n"
            "**Yechim:** Google AI Studio'dan tekin Gemini kaliti olib ishlatsangiz, botingiz 100% barqaror ishlaydi.\n\n"
            f"Oxirgi xatolik: {last_error[:40]}..."
        )

    else:
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Savolga o'zbek tilida javob ber."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Xatolik (OpenAI): {str(e)}"


