import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.reply import BTN_ADD_DEAL
from states.deal_states import DealAddState

from sqlalchemy import select
from database.db import async_session
from database.models import User

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.models import Base

logger = logging.getLogger(__name__)
router = Router()

# === Дополняем модель: создаём таблицу deals ===
class Deal(Base):
    """
    Таблица сделок пользователя.
    """
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="Открыта")

# === Шаг 1: начало ===
@router.message(Command("add_deal"))
@router.message(F.text == BTN_ADD_DEAL)
async def add_deal_start(message: Message, state: FSMContext):
    """
    Точка входа: спрашиваем название сделки.
    """
    await state.set_state(DealAddState.waiting_for_title)
    await message.answer("Введите название сделки (например: Сделка с ООО Ромашка):")

# === Шаг 2: сумма ===
@router.message(DealAddState.waiting_for_title, F.text.len() > 0)
async def add_deal_get_amount(message: Message, state: FSMContext):
    """
    Получаем название, просим сумму сделки.
    """
    await state.update_data(title=message.text.strip())
    await state.set_state(DealAddState.waiting_for_amount)
    await message.answer("Введите сумму сделки (например: 85000):")

# === Шаг 3: выбор статуса (inline кнопки) ===
@router.message(DealAddState.waiting_for_amount, F.text.regexp(r"^\d+$"))
async def add_deal_choose_status(message: Message, state: FSMContext):
    """
    Получаем сумму и предлагаем выбрать статус через inline-кнопки.
    """
    await state.update_data(amount=int(message.text.strip()))

    builder = InlineKeyboardBuilder()
    for status in ["Открыта", "В процессе", "Закрыта"]:
        builder.button(text=status, callback_data=f"deal_status:{status}")
    builder.adjust(1)

    await state.set_state(DealAddState.waiting_for_status)
    await message.answer("Выберите статус сделки:", reply_markup=builder.as_markup())

# === Шаг 4: обработка статуса и сохранение ===
@router.callback_query(F.data.startswith("deal_status:"))
async def add_deal_save(callback: CallbackQuery, state: FSMContext):
    """
    Сохраняем сделку в базу данных после выбора статуса.
    """
    status = callback.data.split(":")[1]
    data = await state.get_data()
    title = data.get("title")
    amount = data.get("amount")
    tg_user = callback.from_user

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

        # сохраняем сделку
        deal = Deal(user_id=user.id, title=title, amount=amount, status=status)
        session.add(deal)
        await session.commit()

    await state.clear()
    await callback.message.answer(
        f"✅ Сделка сохранена:\n• {title}\n• Сумма: {amount} ₽\n• Статус: {status}"
    )
    await callback.answer()
    logger.info(
        "Deal created for user %s: %s | %s₽ | %s",
        tg_user.id, title, amount, status
    )

# === Отмена ===
@router.message(Command("cancel"))
async def cancel_deal(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Возврат в главное меню.")
