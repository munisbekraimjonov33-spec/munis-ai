from aiogram import Router, types
from aiogram.types import Message
from loader import db
from utils.ai import get_ai_response
from datetime import datetime

router = Router()

@router.message()
async def bot_message(message: Message):
    user_id = message.from_user.id
    user = db.select_user(id=user_id)
    
    if not user:
        # Should be caught by start, but just in case
        db.add_user(user_id, message.from_user.full_name)
        user = db.select_user(id=user_id) # columns: id, name, user, date, pro, daily, last
    
    # User tuple unpacking (sqlite returns tuple)
    # id=0, full_name=1, username=2, join=3, pro=4, daily=5, last=6
    is_pro = user[4]
    daily_requests = user[5]
    last_request_date = user[6]
    today = str(datetime.now().date())

    # Reset limit if new day
    if last_request_date != today:
        daily_requests = 0
        db.update_user_daily_limit(user_id, 0, today)
    
    # Check limits
    if not is_pro and daily_requests >= 10:
        await message.answer("Sizning kunlik bepul so'rovlaringiz tugadi (10 ta).\nCheksiz foydalanish uchun Pro obuna sotib oling.\nNarxi: 10 000 so'm.\nInfo: /pro")
        return

    # Process request
    wait_msg = await message.answer("...")
    response = await get_ai_response(message.text)
    await wait_msg.delete()
    await message.answer(response)
    
    # Increment counter
    db.update_user_daily_limit(user_id, daily_requests + 1, today)
