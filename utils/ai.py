import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
import asyncio
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
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-7b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "deepseek/deepseek-chat:free",
    "gryphe/mythomax-l2-13b:free"
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
        for model_name in OPENROUTER_MODELS:
            for attempt in range(2): # Try each model up to 2 times
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. Savolga o'zbek tilida javob ber."},
                            {"role": "user", "content": text}
                        ],
                        timeout=45 # Increased timeout
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg:
                        if attempt == 0:
                            await asyncio.sleep(3) # Wait slightly longer
                            continue
                        else:
                            print(f"Model {model_name} rate limited, trying next...")
                            break
                    else:
                        print(f"Error with {model_name}: {error_msg}")
                        break
        return "Hozirda AI xizmatlarining barchasi juda band. Iltimos, bir ozdan so'ng (masalan, 15 soniyadan keyin) qayta urinib ko'ring. Men sizga yordam berishni juda xohlayman! 😊"

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


