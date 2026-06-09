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
from aiogram.filters import Command

# Kino qo'shish uchun admin buyrug'i
@dp.message(Command("add"))
async def add_film(message: types.Message):
    # Faqat admin ishlata oladi
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Bu buyruq faqat admin uchun!")
        return
    
    # /add kod kanal_id film_nomi
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("❌ Format: /add <kod> <kanal_video_id> <film_nomi>\nMasalan: /add kino123 -100123456789 Kinoning nomi")
            return
        
        kod = parts[1]
        channel_video_id = parts[2].split(" ", 1)[0]
        film_nomi = parts[2].split(" ", 1)[1] if " " in parts[2] else "Nomsiz"
        
        conn = sqlite3.connect('films.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO films (kod, channel_video_id, film_nomi) VALUES (?, ?, ?)", 
                       (kod, channel_video_id, film_nomi))
        conn.commit()
        conn.close()
        
        await message.answer(f"✅ Kino qo'shildi!\nKod: {kod}\nNomi: {film_nomi}")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
