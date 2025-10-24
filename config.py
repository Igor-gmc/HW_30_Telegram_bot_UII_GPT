import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
import re

# --- Путь к .env рядом с этим файлом ---
BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / ".env"

# --- Грузим .env из фиксированного пути ---
load_dotenv(dotenv_path=DOTENV_PATH)

# --- Логи ---
LOG_DIR = str(BASE_DIR / "logs")

def setup_logging():
    """
    Очищает папку logs и настраивает логирование.
    Лимит файла 10 МБ, без бэкапов.
    """
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "bot.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=0
    )
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if root.hasHandlers():
        root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(logging.StreamHandler())

    logging.info("🧹 Логи очищены и инициализированы.")

# --- Переменные окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.getenv("POSTGRES_DB", "assistant_bot")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# --- Валидация токена (как у BotFather: digits:Base64-like) ---
_TOKEN_RE = re.compile(r"^\d{6,12}:[A-Za-z0-9_-]{20,}$")

def validate_bot_token_or_raise(token: str) -> None:
    """
    Проверяет, что токен выглядит как валидный Telegram Bot API токен.
    Бросает ValueError с понятным текстом, если токен пустой или кривой.
    """
    if not token:
        raise ValueError(
            "BOT_TOKEN пуст. Проверь .env (ключ BOT_TOKEN=...) или переменные окружения."
        )
    if not _TOKEN_RE.match(token.strip()):
        # Маскируем токен в логах
        masked = token[:6] + "..." if len(token) >= 6 else "***"
        raise ValueError(
            f"BOT_TOKEN выглядит некорректно: '{masked}'. "
            "Скопируй токен заново из @BotFather без пробелов и кавычек."
        )
