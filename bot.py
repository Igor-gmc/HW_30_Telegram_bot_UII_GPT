import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, setup_logging, validate_bot_token_or_raise
from database.models import Base
from database.db import engine

# 🔽 добавляем импорт роутера
from handlers.start import router as start_router

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
    - регистрация маршрутов
    - запуск polling
    """
    setup_logging()
    validate_bot_token_or_raise(BOT_TOKEN)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # 🔽 регистрируем /start
    dp.include_router(start_router)

    await on_startup()
    logger.info("🤖 Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
