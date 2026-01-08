from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
from database import Database

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = os.getenv("ADMINS").split(",")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "munisbek2828")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database(path_to_db="main.db")
