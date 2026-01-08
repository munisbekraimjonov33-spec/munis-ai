import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def echo_handler(message: types.Message):
    print("------------------------------------------------")
    print(f"Message from: {message.chat.title} ({message.chat.type})")
    print(f"Chat ID: {message.chat.id}")
    if message.forward_from_chat:
        print(f"Forwarded from Channel Name: {message.forward_from_chat.title}")
        print(f"Forwarded from Channel ID: {message.forward_from_chat.id}")
    print("------------------------------------------------")
    await message.answer(f"ID: `{message.chat.id}`\nAgar kanaldan forward qilgan bo'lsangiz terminalga qarang.")

async def main():
    print("Bot ishga tushdi. Kanal ID sini bilish uchun:")
    print("1. Kanalga kiring.")
    print("2. Istalgan xabarni shu botga Forward qiling.")
    print("3. Terminalda 'Forwarded from Channel ID' ni ko'ring.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
