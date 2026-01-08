from aiogram import Router, types
from aiogram.filters import CommandStart
from loader import db
from datetime import datetime

router = Router()

@router.message(CommandStart())
async def bot_start(message: types.Message):
    full_name = message.from_user.full_name
    username = message.from_user.username
    user_id = message.from_user.id
    
    # Add user to DB
    try:
        db.add_user(id=user_id, full_name=full_name, username=username, join_date=datetime.now().date())
    except:
        pass # User likely exists
        
    await message.answer(f"Assalomu alaykum, {full_name}!\n\nMen sun'iy intellekt botman. Savolingizni yozing.")
