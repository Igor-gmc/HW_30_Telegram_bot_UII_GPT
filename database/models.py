from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass

class User(Base):
    """
    Таблица пользователей бота.
    Каждый пользователь Telegram создаётся при первом взаимодействии с ботом.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True)         # Telegram ID пользователя
    username: Mapped[str] = mapped_column(String(100))      # username или имя
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

class Task(Base):
    """
    Таблица задач пользователя.
    Связана с таблицей users через user_id (внешний ключ).
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # ссылка на пользователя
    title: Mapped[str] = mapped_column(String(255))               # название задачи
    time: Mapped[str] = mapped_column(String(50))                 # время выполнения
    status: Mapped[str] = mapped_column(
        String(50), default="Не выполнена"
    )                                                             # текущий статус