from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from config import ADMIN_ID, MOVIES_CHANNEL_ID
from database import (
    get_channels, add_channel, remove_channel,
    add_movie, delete_movie, get_all_movies, get_movie,
    get_user_count
)

router = Router()


def is_admin(message: types.Message) -> bool:
    return message.from_user.id == ADMIN_ID


class AddChannel(StatesGroup):
    channel_id = State()
    channel_name = State()
    channel_link = State()

class AddMovie(StatesGroup):
    code = State()
    title = State()
    description = State()
    year = State()
    genre = State()
    message_id = State()

class DeleteMovie(StatesGroup):
    code = State()


def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Kanallar"), KeyboardButton(text="🎬 Filmlar")],
            [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="➖ Kanal o'chirish")],
            [KeyboardButton(text="🎥 Film qo'shish"), KeyboardButton(text="🗑 Film o'chirish")],
            [KeyboardButton(text="📊 Statistika")],
        ],
        resize_keyboard=True
    )


@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message):
        return
    await message.answer("👑 *Admin Panel*", parse_mode="Markdown", reply_markup=admin_keyboard())


@router.message(F.text == "📢 Kanallar")
async def list_channels(message: types.Message):
    if not is_admin(message):
        return
    channels = await get_channels()
    if not channels:
        await message.answer("Hozircha majburiy kanallar yo'q.")
        return
    text = "📢 *Majburiy kanallar:*\n\n"
    for ch in channels:
        text += f"• {ch['channel_name']} | `{ch['channel_id']}`\n"
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "➕ Kanal qo'shish")
async def start_add_channel(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await message.answer("Kanal ID sini yuboring:\n(Masalan: `-1001234567890`)\n\n/bekor — bekor qilish")
    await state.set_state(AddChannel.channel_id)

@router.message(AddChannel.channel_id)
async def add_channel_id(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(channel_id=message.text.strip())
    await message.answer("Kanal nomini yuboring:")
    await state.set_state(AddChannel.channel_name)

@router.message(AddChannel.channel_name)
async def add_channel_name(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(channel_name=message.text.strip())
    await message.answer("Kanal linkini yuboring:\n(Masalan: `https://t.me/kanalname`)")
    await state.set_state(AddChannel.channel_link)

@router.message(AddChannel.channel_link)
async def add_channel_link(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    data = await state.get_data()
    await add_channel(data["channel_id"], data["channel_name"], message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Kanal qo'shildi: *{data['channel_name']}*",
        parse_mode="Markdown",
        reply_markup=admin_keyboard()
    )


@router.message(F.text == "➖ Kanal o'chirish")
async def start_remove_channel(message: types.Message):
    if not is_admin(message):
        return
    channels = await get_channels()
    if not channels:
        await message.answer("O'chiriladigan kanal yo'q.")
        return
    buttons = [[InlineKeyboardButton(
        text=f"🗑 {ch['channel_name']}",
        callback_data=f"delch_{ch['channel_id']}"
    )] for ch in channels]
    await message.answer("O'chiriladigan kanalni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("delch_"))
async def confirm_remove_channel(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    channel_id = callback.data.replace("delch_", "")
    await remove_channel(channel_id)
    await callback.answer("✅ Kanal o'chirildi!", show_alert=True)
    await callback.message.edit_text(f"✅ Kanal o'chirildi: `{channel_id}`", parse_mode="Markdown")


@router.message(F.text == "🎥 Film qo'shish")
async def start_add_movie(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await message.answer("Film *kodini* yuboring:\n/bekor — bekor qilish", parse_mode="Markdown")
    await state.set_state(AddMovie.code)

@router.message(AddMovie.code)
async def add_movie_code(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    existing = await get_movie(message.text.strip())
    if existing:
        await message.answer("⚠️ Bu kod allaqachon mavjud! Boshqa kod kiriting.")
        return
    await state.update_data(code=message.text.strip())
    await message.answer("Film *nomini* yuboring:", parse_mode="Markdown")
    await state.set_state(AddMovie.title)

@router.message(AddMovie.title)
async def add_movie_title(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(title=message.text.strip())
    await message.answer("Film *tavsifini* yuboring: (o'tkazish uchun `-`)", parse_mode="Markdown")
    await state.set_state(AddMovie.description)

@router.message(AddMovie.description)
async def add_movie_desc(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(description=None if message.text.strip() == "-" else message.text.strip())
    await message.answer("Film *yilini* yuboring: (o'tkazish uchun `-`)", parse_mode="Markdown")
    await state.set_state(AddMovie.year)

@router.message(AddMovie.year)
async def add_movie_year(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(year=None if message.text.strip() == "-" else message.text.strip())
    await message.answer("Film *janrini* yuboring: (o'tkazish uchun `-`)", parse_mode="Markdown")
    await state.set_state(AddMovie.genre)

@router.message(AddMovie.genre)
async def add_movie_genre(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    await state.update_data(genre=None if message.text.strip() == "-" else message.text.strip())
    await message.answer(
        "Kanalingizdagi xabarning *message_id* sini yuboring:\n"
        "(@JsonDumpBot orqali bilib olish mumkin)",
        parse_mode="Markdown"
    )
    await state.set_state(AddMovie.message_id)

@router.message(AddMovie.message_id)
async def add_movie_msgid(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    if not message.text.strip().isdigit():
        await message.answer("⚠️ Message ID faqat raqam bo'lishi kerak!")
        return
    data = await state.get_data()
    await add_movie(
        code=data["code"],
        title=data["title"],
        description=data.get("description"),
        year=data.get("year"),
        genre=data.get("genre"),
        message_id=int(message.text.strip())
    )
    await state.clear()
    await message.answer(
        f"✅ Film qo'shildi!\n🎬 *{data['title']}* | Kod: `{data['code']}`",
        parse_mode="Markdown",
        reply_markup=admin_keyboard()
    )


@router.message(F.text == "🗑 Film o'chirish")
async def start_delete_movie(message: types.Message, state: FSMContext):
    if not is_admin(message):
        return
    await message.answer("O'chiriladigan filmning *kodini* yuboring:\n/bekor — bekor qilish", parse_mode="Markdown")
    await state.set_state(DeleteMovie.code)

@router.message(DeleteMovie.code)
async def delete_movie_handler(message: types.Message, state: FSMContext):
    if message.text == "/bekor":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return
    movie = await get_movie(message.text.strip())
    if not movie:
        await message.answer("❌ Bunday kodli film topilmadi.")
        await state.clear()
        return
    await delete_movie(message.text.strip())
    await state.clear()
    await message.answer(f"✅ *{movie['title']}* o'chirildi.", parse_mode="Markdown", reply_markup=admin_keyboard())


@router.message(F.text == "🎬 Filmlar")
async def list_movies(message: types.Message):
    if not is_admin(message):
        return
    movies = await get_all_movies()
    if not movies:
        await message.answer("Hozircha filmlar yo'q.")
        return
    text = f"🎬 *Jami: {len(movies)} ta film*\n\n"
    for m in movies[:30]:
        text += f"• `{m['code']}` — {m['title']}\n"
    if len(movies) > 30:
        text += f"\n...va yana {len(movies) - 30} ta."
    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "📊 Statistika")
async def statistics(message: types.Message):
    if not is_admin(message):
        return
    movies = await get_all_movies()
    channels = await get_channels()
    users_count = await get_user_count()
    await message.answer(
        f"📊 *Statistika:*\n\n"
        f"👤 Foydalanuvchilar: *{users_count} ta*\n"
        f"🎬 Filmlar: *{len(movies)} ta*\n"
        f"📢 Kanallar: *{len(channels)} ta*",
        parse_mode="Markdown"
    )
