import sqlite3
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =================== SOZLAMALAR ==================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6756923304
CHANNEL_ID = -1003721029830

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Vaqtinchalik ma'lumotlar
temp_kod = None
temp_nom = None

def init_db():
    conn = sqlite3.connect('films.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS films (
    kod TEXT PRIMARY KEY,
    channel_video_id TEXT,
    film_nomi TEXT
    ''')
    conn.commit()
    conn.close()

print("Baza tayyor")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Assalomu alaykum! Kino kodini yuboring.")
