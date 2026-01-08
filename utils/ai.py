import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from openai import OpenAI
from loader import OPENAI_API_KEY

# Determine which provider to use
USE_GEMINI = OPENAI_API_KEY.startswith("AIza")

if USE_GEMINI:
    genai.configure(api_key=OPENAI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

async def get_ai_response(text: str) -> str:
    try:
        if USE_GEMINI:
            # Gemini Call
            prompt = (
                "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. "
                "Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. "
                f"Savolga o'zbek tilida javob ber.\n\nFoydalanuvchi: {text}"
            )
            response = model.generate_content(prompt)
            return response.text
        else:
            # OpenAI Call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen 'Munis AI' ismli yordamchisan. Javoblaring qisqa, lo'nda va samimiy, xuddi odam kabi tabiiy bo'lsin. Har bir javobda qonun haqida gapirma, faqat noqonuniy narsa so'ralsa rad et. Savolga o'zbek tilida javob ber."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Xatolik: {str(e)}"
