from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import logging

# Создаём отдельный логгер для работы с базой данных
logger = logging.getLogger(__name__)

# --- Асинхронный движок SQLAlchemy ---
# echo=False — отключает лишние SQL-логи в консоли
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# --- Фабрика асинхронных сессий ---
# expire_on_commit=False — данные не будут очищаться после commit
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    """
    Асинхронный генератор сессий к базе данных.
    Каждый раз, когда вызывается функция, создаётся новая сессия.
    После завершения работы сессия автоматически закрывается.
    
    Пример использования:
        async for session in get_session():
            await session.execute(...)
    """
    async with async_session() as session:
        yield session
