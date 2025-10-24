import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, setup_logging, validate_bot_token_or_raise
from database.models import Base
from database.db import engine

logger = logging.getLogger(__name__)

async def on_startup():
    """
    Создаёт таблицы в БД при первом запуске.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Таблицы успешно созданы (если их не было).")

async def main():
    """
    Точка входа:
    - логирование
    - валидация токена
    - инициализация бота и БД
    - запуск polling
    """
    setup_logging()

    # Валидация токена до создания Bot(...)
    validate_bot_token_or_raise(BOT_TOKEN)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await on_startup()
    logger.info("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
