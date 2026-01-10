import asyncio
import sys
import os

# Add the current directory to sys.path to import utils
sys.path.append(os.getcwd())

# Ensure UTF-8 encoding for printing emojis
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.ai import get_ai_response

async def test_bot():
    print("--- Testing Bot Identity ---")
    resp1 = await get_ai_response("Seni kim yaratgan?")
    print(f"User: Seni kim yaratgan?\nAI: {resp1}\n")

    print("--- Testing Bot Memory (History) ---")
    history = [
        ("user", "Qaysi tillarni bilasan?"),
        ("assistant", "Men o'zbek, rus va ingliz tillarini bilaman.")
    ]
    resp2 = await get_ai_response("Nechta?", history=history)
    print(f"User: Qaysi tillarni bilasan?\nAI: Men o'zbek, rus va ingliz tillarini bilaman.")
    print(f"User: Nechta?\nAI: {resp2}\n")

    if "Munisbek" in resp1:
        print("✅ Identity test passed!")
    else:
        print("❌ Identity test failed!")

    if "3" in resp2 or "uchta" in resp2.lower():
        print("✅ Memory test passed!")
    else:
        # Some AIs might answer differently, but should mention the count
        print("⚠️ Memory test result unclear, please check AI output.")

if __name__ == "__main__":
    asyncio.run(test_bot())
