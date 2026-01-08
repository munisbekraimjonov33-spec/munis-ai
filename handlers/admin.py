from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loader import db, ADMINS, ADMIN_PASSWORD
from handlers.states import AdminAuth

router = Router()

# Authenticated admin sessions (in-memory, resets on bot restart)
authenticated_admins = set()

@router.message(Command("pro"))
async def buy_pro(message: types.Message):
    await message.answer("Pro obuna - 10 000 so'm.\nCheksiz so'rovlar.\nSotib olish uchun admin bilan bog'laning: @Munisbek_Raimjonov")

@router.message(Command("admin"))
async def admin_panel(message: types.Message, state: FSMContext):
    if str(message.from_user.id) not in ADMINS:
        return
    
    # Check if already authenticated
    if message.from_user.id in authenticated_admins:
        await message.answer("Admin panel:\n/royxat - Foydalanuvchilar ro'yxati\n/add_pro [id] - Pro berish\n/del_pro [id] - Pro olish\n/stats - Statistika\n/logout - Chiqish")
        return
    
    # Request password
    await message.answer("Admin panelga kirish uchun parolni kiriting:")
    await state.set_state(AdminAuth.waiting_for_password)

@router.message(AdminAuth.waiting_for_password)
async def check_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        authenticated_admins.add(message.from_user.id)
        await state.clear()
        await message.answer("✅ Muvaffaqiyatli kirdingiz!\n\nAdmin panel:\n/royxat - Foydalanuvchilar ro'yxati\n/add_pro [id] - Pro berish\n/del_pro [id] - Pro olish\n/stats - Statistika\n/logout - Chiqish")
    else:
        await message.answer("❌ Parol noto'g'ri! Qaytadan urinib ko'ring: /admin")
        await state.clear()

@router.message(Command("royxat"))
async def list_users(message: types.Message):
    if str(message.from_user.id) not in ADMINS or message.from_user.id not in authenticated_admins:
        return
    
    users = db.get_all_users()
    if not users:
        await message.answer("Hech qanday foydalanuvchi topilmadi.")
        return
    
    # Format user list
    user_list = "📋 Foydalanuvchilar ro'yxati:\n\n"
    for user_id, full_name in users:
        user_list += f"👤 {full_name}\n   ID: <code>{user_id}</code>\n\n"
    
    user_list += "\n💡 Pro berish uchun: /add_pro [ID]"
    
    await message.answer(user_list, parse_mode="HTML")

@router.message(Command("logout"))
async def logout_admin(message: types.Message):
    if message.from_user.id in authenticated_admins:
        authenticated_admins.remove(message.from_user.id)
        await message.answer("Chiqish amalga oshirildi.")
    else:
        await message.answer("Siz tizimga kirmagansiz.")

@router.message(Command("add_pro"))
async def add_pro(message: types.Message):
    if str(message.from_user.id) not in ADMINS or message.from_user.id not in authenticated_admins:
        return
    try:
        user_id = int(message.text.split()[1])
        db.set_pro_status(user_id, True)
        await message.answer(f"Foydalanuvchi {user_id} ga Pro berildi.")
        await message.bot.send_message(user_id, "Sizga Pro obuna faollashtirildi! Endi cheksiz savol berishingiz mumkin.")
    except:
        await message.answer("Xato! Format: /add_pro 12345678")

@router.message(Command("del_pro"))
async def remove_pro(message: types.Message):
    if str(message.from_user.id) not in ADMINS or message.from_user.id not in authenticated_admins:
        return
    try:
        user_id = int(message.text.split()[1])
        db.set_pro_status(user_id, False)
        await message.answer(f"Foydalanuvchi {user_id} dan Pro olindi.")
    except:
        await message.answer("Xato! Format: /del_pro 12345678")

@router.message(Command("stats"))
async def show_stats(message: types.Message):
    if str(message.from_user.id) not in ADMINS or message.from_user.id not in authenticated_admins:
        return
    count = db.count_users()[0]
    await message.answer(f"Jami foydalanuvchilar: {count}")
