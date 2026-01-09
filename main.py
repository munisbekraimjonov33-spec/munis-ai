import asyncio
import logging
import sys
import os
from aiohttp import web
from loader import dp, bot, db
from handlers import router as main_router
from middlewares.subscription import SubscriptionMiddleware

# Simple web server to satisfy Render's port requirement
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    # Get port from environment variable, default to 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    # Logging configuration
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Create DB tables
    db.create_table_users()
    
    # Register Middleware
    dp.message.middleware(SubscriptionMiddleware())
    
    # Register Handlers
    dp.include_router(main_router)
    
    # Start Web Server in background
    await start_web_server()
    
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
