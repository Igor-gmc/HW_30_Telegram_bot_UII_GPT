import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.reply import BTN_ADD_TASK, BTN_VIEW_TASKS
from states.task_states import TaskAddState

from sqlalchemy import select, delete
from database.db import async_session
from database.models import User, Task

router = Router()
logger = logging.getLogger(__name__)

# === Добавление задачи ===

@router.message(Command("add_task"))
@router.message(F.text == BTN_ADD_TASK)
async def add_task_start(message: Message, state: FSMContext) -> None:
    """
    Точка входа в мастер добавления задачи.
    Просим у пользователя название задачи.
    """
    await state.set_state(TaskAddState.waiting_for_title)
    await message.answer("Введите название задачи (например: Подготовить КП):")


@router.message(TaskAddState.waiting_for_title, F.text.len() > 0)
async def add_task_get_title(message: Message, state: FSMContext) -> None:
    """
    Сохраняем название задачи во временном состоянии и просим время.
    """
    await state.update_data(title=message.text.strip())
    await state.set_state(TaskAddState.waiting_for_time)
    await message.answer("Укажите время выполнения (например: 18:00):")


@router.message(TaskAddState.waiting_for_time, F.text.len() > 0)
async def add_task_save(message: Message, state: FSMContext) -> None:
    """
    Получаем время, создаём пользователя (если его ещё нет) и сохраняем задачу в БД.
    """
    time_text = message.text.strip()
    data = await state.get_data()
    title = data.get("title")

    if len(time_text) > 50:
        await message.answer("Слишком длинное время. Укажите, например: 18:00")
        return

    tg_user = message.from_user

    async with async_session() as session:
        # находим/создаём пользователя
        result = await session.execute(
            select(User).where(User.tg_id == tg_user.id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(tg_id=tg_user.id, username=tg_user.username or "")
            session.add(user)
            await session.flush()

        # создаём задачу
        task = Task(user_id=user.id, title=title, time=time_text, status="Не выполнена")
        session.add(task)
        await session.commit()

    await state.clear()
    await message.answer(f"✅ Задача сохранена:\n• {title}\n• Время: {time_text}")
    logger.info("Task created for user %s: %s at %s", tg_user.id, title, time_text)


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    """
    Отмена мастера добавления задачи. Очищаем состояние.
    """
    await state.clear()
    await message.answer("Отменено. Возврат в главное меню.")


# --- NEW CODE START: просмотр и сортировка задач ---

@router.message(F.text == BTN_VIEW_TASKS)
@router.message(Command("view_tasks"))
async def view_tasks(message: Message):
    """
    Показывает пользователю список задач.
    Незавершённые задачи идут первыми, завершённые — внизу списка.
    """
    tg_user = message.from_user

    async with async_session() as session:
        result = await session.execute(
            select(Task).join(User).where(User.tg_id == tg_user.id)
        )
        tasks = result.scalars().all()

    if not tasks:
        await message.answer("У вас пока нет задач.")
        return

    # --- NEW CODE START: сортировка ---
    tasks.sort(key=lambda t: 0 if t.status != "Выполнена" else 1)
    # --- NEW CODE END ---

    text = "📋 <b>Ваши задачи:</b>\n\n"
    builder = InlineKeyboardBuilder()

    for task in tasks:
        text += f"• <b>{task.title}</b> — {task.time} [{task.status}]\n"
        builder.button(text=f"✅ {task.id}", callback_data=f"task_done:{task.id}")
        builder.button(text=f"🗑 {task.id}", callback_data=f"task_del:{task.id}")

    builder.adjust(2)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# --- NEW CODE END ---


@router.callback_query(F.data.startswith("task_done:"))
async def mark_task_done(callback: CallbackQuery):
    """
    Переключает статус задачи: Выполнена <-> Не выполнена.
    """
    task_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task:
            task.status = "Выполнена" if task.status != "Выполнена" else "Не выполнена"
            await session.commit()
            await callback.answer(f"Статус изменён на «{task.status}» ✅")
        else:
            await callback.answer("Задача не найдена ❌", show_alert=True)


@router.callback_query(F.data.startswith("task_del:"))
async def delete_task(callback: CallbackQuery):
    """
    Удаляет задачу из базы данных.
    """
    task_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        await session.execute(delete(Task).where(Task.id == task_id))
        await session.commit()
    await callback.answer("Задача удалена 🗑")
    await callback.message.edit_text("Задача удалена. Обновите список 📋")
