import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import asyncio
import random
import logging
import os
from openai import AsyncOpenAI
from loader import OPENAI_API_KEYS

async def get_ai_response(text: str, history: list = None) -> str:
    if not OPENAI_API_KEYS:
        return "Xatolik: Hech qanday API kalit topilmadi. .env faylini tekshiring."

    if history is None:
        history = []

    # Identity and System Prompt
    system_instruction = (
        "Seni Munisbek Raimjonov yaratgan. Sen profesisonal AI yordamchisan. "
        "Foydalanuvchi savollariga faqat o'zbek tilida, aniq va foydali javob ber. "
        "Munisbek Raimjonov haqida so'rashsa, u mening yaratuvchim deb javob ber. "
        "Suhbat tarixini eslab qol va oldingi gaplarga tayanib javob ber."
    )

    # Shuffle keys to distribute load
    shuffled_keys = list(OPENAI_API_KEYS)
    random.shuffle(shuffled_keys)

    last_error = ""
    # Try each key in the shuffled list
    for api_key in shuffled_keys:
        # Retry mechanism for each key
        for attempt in range(2):
            try:
                # Determine provider for this specific key
                is_gemini = api_key.startswith("AIza")
                is_openrouter = api_key.startswith("sk-or-")

                if is_gemini:
                    try:
                        genai.configure(api_key=api_key)
                        # More resilient model list
                        gemini_models = [
                            'models/gemini-1.5-flash-latest', 
                            'models/gemini-1.5-pro-latest', 
                            'models/gemini-flash-latest',
                            'models/gemini-pro-latest'
                        ]
                        
                        for model_name in gemini_models:
                            try:
                                model = genai.GenerativeModel(
                                    model_name=model_name,
                                    system_instruction=system_instruction
                                )
                                chat_history = []
                                for role, content in history:
                                    chat_history.append({"role": "user" if role == "user" else "model", "parts": [content]})
                                
                                chat = model.start_chat(history=chat_history)
                                loop = asyncio.get_event_loop()
                                response = await loop.run_in_executor(None, lambda: chat.send_message(text))
                                return response.text
                            except Exception as e:
                                last_error = str(e)
                                if "429" in last_error: break # Move to next key if rate limited
                                continue
                    except Exception as e:
                        last_error = str(e)
                        continue

                elif is_openrouter:
                    client = AsyncOpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )
                    
                    messages = [{"role": "system", "content": system_instruction}]
                    for role, content in history:
                        messages.append({"role": role, "content": content})
                    messages.append({"role": "user", "content": text})

                    # Expanded list of free models
                    openrouter_models = [
                        "google/gemini-2.0-flash-exp:free",
                        "google/gemini-flash-1.5-exp:free",
                        "meta-llama/llama-3.3-70b-instruct:free",
                        "meta-llama/llama-3.1-8b-instruct:free",
                        "mistralai/mistral-7b-instruct:free",
                        "qwen/qwen-2-7b-instruct:free",
                        "microsoft/phi-3-mini-128k-instruct:free",
                        "gryphe/mythomax-l2-13b:free"
                    ]
                    random.shuffle(openrouter_models)

                    for model_name in openrouter_models:
                        try:
                            response = await client.chat.completions.create(
                                model=model_name,
                                messages=messages,
                                timeout=20
                            )
                            return response.choices[0].message.content
                        except Exception as e:
                            last_error = str(e)
                            if "429" in last_error: break # Move to next key if rate limited
                            continue

                else:
                    # Default OpenAI
                    client = AsyncOpenAI(api_key=api_key)
                    messages = [{"role": "system", "content": system_instruction}]
                    for role, content in history:
                        messages.append({"role": role, "content": content})
                    messages.append({"role": "user", "content": text})

                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        timeout=30
                    )
                    return response.choices[0].message.content

            except Exception as e:
                last_error = str(e)
                if attempt == 0: await asyncio.sleep(1)
                continue

    # Final User-Friendly Fallback
    return (
        "Hozirda botga juda ko'p so'rovlar kelmoqda. 😅\n"
        "Iltimos, 1 daqiqadan so'ng qayta urinib ko'ring.\n\n"
        "Muallif: Munisbek Raimjonov"
    )


