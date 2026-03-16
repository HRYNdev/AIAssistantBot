import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.config import settings
from bot.db import init_db
from bot.knowledge import load_knowledge_base
from bot.handlers import chat, admin

logging.basicConfig(level=logging.INFO)


async def main():
    init_db()
    load_knowledge_base()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(admin.router)  # admin first to intercept /reload, /gaps
    dp.include_router(chat.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
