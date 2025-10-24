import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply import BTN_ADD_TASK
from states.task_states import TaskAddState

from sqlalchemy import select
from database.db import async_session
from database.models import User, Task

router = Router()
logger = logging.getLogger(__name__)

# === Старт добавления задачи ===
@router.message(Command("add_task"))
@router.message(F.text == BTN_ADD_TASK)
async def add_task_start(message: Message, state: FSMContext) -> None:
    """
    Точка входа в мастер добавления задачи.
    Просим у пользователя название задачи.
    """
    await state.set_state(TaskAddState.waiting_for_title)
    await message.answer("Введите название задачи (например: Подготовить КП):")

# === Получаем название задачи и спрашиваем время ===
@router.message(TaskAddState.waiting_for_title, F.text.len() > 0)
async def add_task_get_title(message: Message, state: FSMContext) -> None:
    """
    Сохраняем название задачи во временном состоянии и просим время.
    """
    await state.update_data(title=message.text.strip())
    await state.set_state(TaskAddState.waiting_for_time)
    await message.answer("Укажите время выполнения (например: 18:00):")

# === Валидируем и сохраняем задачу в БД ===
@router.message(TaskAddState.waiting_for_time, F.text.len() > 0)
async def add_task_save(message: Message, state: FSMContext) -> None:
    """
    Получаем время, создаём пользователя (если его ещё нет) и сохраняем задачу в БД.
    """
    time_text = message.text.strip()
    data = await state.get_data()
    title = data.get("title")

    # Мини-валидация времени — оставим в виде строки (форматируем позже)
    if len(time_text) > 50:
        await message.answer("Слишком длинное время. Укажите, например: 18:00")
        return

    tg_user = message.from_user

    async with async_session() as session:
        # 1) находим/создаём пользователя
        result = await session.execute(
            select(User).where(User.tg_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(tg_id=tg_user.id, username=tg_user.username or "")
            session.add(user)
            await session.flush()  # получим user.id без отдельного коммита

        # 2) создаём задачу
        task = Task(user_id=user.id, title=title, time=time_text, status="Не выполнена")
        session.add(task)
        await session.commit()

    await state.clear()
    await message.answer(f"✅ Задача сохранена:\n• {title}\n• Время: {time_text}")
    logger.info("Task created for user %s: %s at %s", tg_user.id, title, time_text)

# === /cancel на любом шаге мастера ===
@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    """
    Отмена мастера добавления задачи. Очищаем состояние.
    """
    await state.clear()
    await message.answer("Отменено. Возврат в главное меню.")
