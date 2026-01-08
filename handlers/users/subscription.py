from aiogram import Router, F, types
from loader import bot, CHANNEL_ID

router = Router()

@router.callback_query(F.data == "check_sub")
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            await call.message.delete()
            await call.message.answer(f"✅ Obuna tasdiqlandi! {call.from_user.full_name}, savol berishingiz mumkin.")
        else:
            await call.answer("❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)
    except Exception as e:
        error_msg = str(e)
        if "chat not found" in error_msg.lower():
            await call.answer("❌ Kanal topilmadi! Kanal ID sini tekshiring (-100...)", show_alert=True)
        elif "bot is not a member" in error_msg.lower():
            await call.answer("❌ Bot kanalga admin qilinmagan! Iltimos, botni kanalga admin qiling.", show_alert=True)
        else:
            await call.answer(f"Xatolik: {error_msg}", show_alert=True)
