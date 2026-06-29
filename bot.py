import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from handlers import user, admin

logging.basicConfig(level=logging.INFO)

async def health(request):
    return web.Response(text="OK")

async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin.router)
    dp.include_router(user.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(
        start_web(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
