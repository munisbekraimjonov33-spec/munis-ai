import asyncio
import logging
import sys
from loader import dp, bot, db
from handlers import router as main_router
from middlewares.subscription import SubscriptionMiddleware

async def main():
    # Logging configuration
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Create DB tables
    db.create_table_users()
    
    # Register Middleware
    dp.message.middleware(SubscriptionMiddleware())
    
    # Register Handlers
    dp.include_router(main_router)
    
    # Start Bot
    try:
        print("\n\n>>> YANGILANGAN BOT ISHGA TUSHDI (v2.0) <<<\n\n")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
