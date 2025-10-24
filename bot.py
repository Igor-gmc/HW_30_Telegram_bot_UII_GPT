import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, setup_logging, validate_bot_token_or_raise
from database.models import Base
from database.db import engine

from handlers.start import router as start_router
from handlers.tasks import router as tasks_router  # 🔽

logger = logging.getLogger(__name__)

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Таблицы успешно созданы (если их не было).")

async def main():
    setup_logging()
    validate_bot_token_or_raise(BOT_TOKEN)

    bot = Bot(token=BOT_TOKEN)

    # 🔽 Явно укажем MemoryStorage для FSM
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(tasks_router)  # 🔽

    await on_startup()
    logger.info("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
