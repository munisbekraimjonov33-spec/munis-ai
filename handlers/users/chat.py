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
        db.add_user(user_id, message.from_user.full_name, message.from_user.username, str(datetime.now().date()))
        user = db.select_user(id=user_id)
    
    is_pro = user[4]
    daily_requests = user[5]
    last_request_date = user[6]
    today = str(datetime.now().date())

    if last_request_date != today:
        daily_requests = 0
        db.update_user_daily_limit(user_id, 0, today)
    
    if not is_pro and daily_requests >= 10:
        await message.answer("Sizning kunlik bepul so'rovlaringiz tugadi (10 ta).\nCheksiz foydalanish uchun Pro obuna sotib oling.\nNarxi: 10 000 so'm.\nInfo: /pro")
        return

    # Professional touch: Show typing status
    from aiogram.utils.chat_action import ChatActionSender
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        # 1. Fetch history
        history = db.get_history(user_id, limit=6) # Get last 6 messages
        
        # 2. Get AI response
        response = await get_ai_response(message.text, history=history)
        
        # 3. Save to history
        db.add_message(user_id, "user", message.text)
        db.add_message(user_id, "assistant", response)
        
        # 4. Reply to user
        await message.answer(response)
    
    # Increment counter
    db.update_user_daily_limit(user_id, daily_requests + 1, today)
