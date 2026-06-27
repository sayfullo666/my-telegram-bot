from aiogram import Router, Bot, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import MOVIES_CHANNEL_ID
from database import get_channels, get_movie

router = Router()


async def check_subscriptions(bot: Bot, user_id: int) -> list:
    channels = await get_channels()
    not_subscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["channel_id"], user_id=user_id)
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(ch)
        except Exception:
            not_subscribed.append(ch)
    return not_subscribed


def subscribe_keyboard(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"📢 {ch['channel_name']}",
            url=ch["channel_link"]
        )])
    buttons.append([InlineKeyboardButton(
        text="✅ Obuna bo'ldim",
        callback_data="check_subscription"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def start_handler(message: types.Message, bot: Bot):
    args = message.text.split()
    if len(args) > 1:
        await handle_movie_request(message, bot, args[1])
        return
    await message.answer(
        "🎬 *Kino Botga Xush Kelibsiz!*\n\n"
        "Film kodini yuboring va kerakli kinoni oling.\n"
        "Masalan: `123`",
        parse_mode="Markdown"
    )


@router.message(F.text.regexp(r'^\d+$'))
async def movie_code_handler(message: types.Message, bot: Bot):
    await handle_movie_request(message, bot, message.text.strip())


async def handle_movie_request(message: types.Message, bot: Bot, code: str):
    user_id = message.from_user.id
    not_subscribed = await check_subscriptions(bot, user_id)
    if not_subscribed:
        await message.answer(
            "⚠️ *Filmni olish uchun quyidagi kanallarga obuna bo'ling:*",
            reply_markup=subscribe_keyboard(not_subscribed),
            parse_mode="Markdown"
        )
        return
    movie = await get_movie(code)
    if not movie:
        await message.answer("❌ Bunday kodli film topilmadi.")
        return
    await send_movie(message, bot, movie)


async def send_movie(message: types.Message, bot: Bot, movie):
    try:
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=MOVIES_CHANNEL_ID,
            message_id=movie["message_id"]
        )
        info = (
            f"🎬 *{movie['title']}*\n"
            f"📅 Yil: {movie['year'] or '—'}\n"
            f"🎭 Janr: {movie['genre'] or '—'}\n"
            f"📝 {movie['description'] or ''}"
        )
        await message.answer(info, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")


@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(callback: types.CallbackQuery, bot: Bot):
    not_subscribed = await check_subscriptions(bot, callback.from_user.id)
    if not_subscribed:
        await callback.answer("❌ Hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=subscribe_keyboard(not_subscribed))
    else:
        await callback.answer("✅ Rahmat! Endi film kodini yuboring.", show_alert=True)
        await callback.message.edit_text("✅ Obuna tasdiqlandi! Endi film kodini yuboring.")
