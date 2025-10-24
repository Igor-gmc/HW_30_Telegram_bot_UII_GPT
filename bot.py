import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# --- Импорты из проекта ---
from config import BOT_TOKEN, setup_logging, validate_bot_token_or_raise
from database.models import Base
from database.db import engine

# --- Импорт хендлеров ---
from handlers.start import router as start_router
from handlers.tasks import router as tasks_router
from handlers.deals import router as deals_router

# --- NEW CODE START: добавлены ChatGPT и отчёт ---
from handlers.marketing import router as marketing_router
from handlers.motivation import router as motivation_router
from handlers.report import router as report_router
# --- NEW CODE END ---

logger = logging.getLogger(__name__)

async def on_startup():
    """
    Создаёт таблицы в БД при первом запуске.
    Если таблицы уже существуют — пропускает.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Таблицы успешно созданы (если их не было).")

async def main():
    """
    Главная точка входа приложения.

    1. Настраивает логирование.
    2. Проверяет валидность BOT_TOKEN.
    3. Инициализирует бота и диспетчер (Dispatcher).
    4. Подключает все роутеры (start, tasks, deals, marketing, motivation, report).
    5. Создаёт таблицы в БД при старте.
    6. Запускает постоянный цикл polling.
    """
    # Настройка логирования
    setup_logging()

    # Проверяем токен
    validate_bot_token_or_raise(BOT_TOKEN)

    # Создаём экземпляр бота и диспетчера
    bot = Bot(token=BOT_TOKEN)

    # Хранилище FSM (в оперативной памяти)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(deals_router)

    # --- NEW CODE START: добавлены модули ChatGPT и отчёт ---
    dp.include_router(marketing_router)
    dp.include_router(motivation_router)
    dp.include_router(report_router)
    # --- NEW CODE END ---

    # Инициализация базы данных
    await on_startup()

    logger.info("🤖 Бот запущен и готов к работе!")
    print(f"Start polling\nRun polling for bot @{(await bot.me()).username}")

    # Запуск бесконечного цикла polling (прослушивание обновлений)
    await dp.start_polling(bot)

# --- Точка входа ---
if __name__ == "__main__":
    """
    При прямом запуске файла bot.py:
    - запускаем event loop через asyncio.run()
    - выполняем асинхронную функцию main()
    """
    asyncio.run(main())
