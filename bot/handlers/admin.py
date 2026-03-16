from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import settings
from bot.db import get_unanswered
from bot.knowledge import load_knowledge_base

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("reload"))
async def cmd_reload(msg: Message):
    if not is_admin(msg.from_user.id):
        return
    await msg.answer("⏳ Загружаю базу знаний...")
    count = load_knowledge_base()
    await msg.answer(f"✅ База знаний обновлена: {count} фрагментов загружено.")


@router.message(Command("gaps"))
async def cmd_gaps(msg: Message):
    """Show questions the bot couldn't answer."""
    if not is_admin(msg.from_user.id):
        return
    rows = get_unanswered(limit=20)
    if not rows:
        await msg.answer("✅ Вопросов без ответа нет.")
        return
    text = "❓ <b>Вопросы без ответа (последние 20):</b>\n\n"
    for i, row in enumerate(rows, 1):
        text += f"{i}. {row['question']}\n"
    await msg.answer(text, parse_mode="HTML")
