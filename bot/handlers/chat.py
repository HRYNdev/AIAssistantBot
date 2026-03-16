from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import settings
from bot.db import add_message, get_history, clear_history, log_unanswered
from bot.knowledge import search
from bot.llm import ask

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        f"👋 Привет! Я помощник компании.\n\n"
        "Задай любой вопрос — я отвечу на основе базы знаний.\n\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/clear — очистить историю диалога"
    )


@router.message(Command("clear"))
async def cmd_clear(msg: Message):
    clear_history(msg.from_user.id)
    await msg.answer("🗑 История очищена.")


@router.message(F.text)
async def handle_question(msg: Message):
    question = msg.text.strip()
    user_id = msg.from_user.id

    await msg.bot.send_chat_action(msg.chat.id, "typing")

    # Search knowledge base
    chunks = search(question, n_results=3)

    # Get conversation history
    history = get_history(user_id, limit=settings.HISTORY_DEPTH)

    # Ask LLM
    answer = await ask(question, chunks, history)

    if "НЕ_ЗНАЮ" in answer:
        reply = (
            "😔 К сожалению, у меня нет информации по этому вопросу.\n\n"
            f"Свяжитесь с менеджером: {settings.SUPPORT_USERNAME}"
        )
        log_unanswered(user_id, question)
    else:
        reply = answer
        # Save to history only successful answers
        add_message(user_id, "user", question)
        add_message(user_id, "assistant", answer)

    await msg.answer(reply)
