from aiogram import Router
from handlers import admin
from handlers.users import start, chat, subscription

router = Router()

# Register admin first
router.include_router(admin.router)

# Register specific user handlers
router.include_router(subscription.router)
router.include_router(start.router)

# Register catch-all chat handler LAST
router.include_router(chat.router)
