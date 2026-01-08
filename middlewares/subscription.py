from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, CHANNEL_ID, CHANNEL_URL

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        user_id = event.from_user.id
        
        # Check subscription
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            if member.status not in ["creator", "administrator", "member"]:
                raise Exception("Not subscribed")
        except Exception as e:
            # Fayl boshida: import logging qo'shish kerak agar yo'q bo'lsa, lekin print ham yetadi hozircha
            print(f"Subscription Check Error: {e}") 
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Obuna bo'lish", url=CHANNEL_URL)],
                [InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
            ])
            await event.answer("Botdan foydalanish uchun kanalimizga obuna bo'ling!", reply_markup=keyboard)
            return

        return await handler(event, data)
