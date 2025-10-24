import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.reply import BTN_ADD_DEAL, BTN_VIEW_DEALS
from states.deal_states import DealAddState
from sqlalchemy import select, delete
from database.db import async_session
from database.models import User, Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

router = Router()
logger = logging.getLogger(__name__)

# === Таблица сделок ===
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

# === Добавление сделки ===

@router.message(Command("add_deal"))
@router.message(F.text == BTN_ADD_DEAL)
async def add_deal_start(message: Message, state: FSMContext):
    await state.set_state(DealAddState.waiting_for_title)
    await message.answer("Введите название сделки (например: Сделка с ООО Ромашка):")


@router.message(DealAddState.waiting_for_title, F.text.len() > 0)
async def add_deal_get_amount(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(DealAddState.waiting_for_amount)
    await message.answer("Введите сумму сделки (например: 85000):")


@router.message(DealAddState.waiting_for_amount, F.text.regexp(r"^\d+$"))
async def add_deal_choose_status(message: Message, state: FSMContext):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    await state.update_data(amount=int(message.text.strip()))
    builder = InlineKeyboardBuilder()
    for status in ["Открыта", "В процессе", "Закрыта"]:
        builder.button(text=status, callback_data=f"deal_status:{status}")
    builder.adjust(1)
    await state.set_state(DealAddState.waiting_for_status)
    await message.answer("Выберите статус сделки:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("deal_status:"))
async def add_deal_save(callback: CallbackQuery, state: FSMContext):
    status = callback.data.split(":")[1]
    data = await state.get_data()
    title = data.get("title")
    amount = data.get("amount")
    tg_user = callback.from_user

    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_user.id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(tg_id=tg_user.id, username=tg_user.username or "")
            session.add(user)
            await session.flush()

        deal = Deal(user_id=user.id, title=title, amount=amount, status=status)
        session.add(deal)
        await session.commit()

    await state.clear()
    await callback.message.answer(
        f"✅ Сделка сохранена:\n• {title}\n• Сумма: {amount} ₽\n• Статус: {status}"
    )
    await callback.answer()
    logger.info("Deal created for user %s: %s | %s₽ | %s", tg_user.id, title, amount, status)


@router.message(Command("cancel"))
async def cancel_deal(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Возврат в главное меню.")

# --- NEW CODE START: просмотр и сортировка сделок ---

@router.message(F.text == BTN_VIEW_DEALS)
@router.message(Command("view_deals"))
async def view_deals(message: Message):
    """
    Показывает список сделок с inline-кнопками:
    🔄 Изменить статус | 🗑 Удалить
    """
    tg_user = message.from_user
    async with async_session() as session:
        result = await session.execute(
            select(Deal).join(User).where(User.tg_id == tg_user.id)
        )
        deals = result.scalars().all()

    if not deals:
        await message.answer("У вас пока нет сделок.")
        return

    # --- NEW CODE START: сортировка по статусу ---
    # Сначала "Открыта" и "В процессе", затем "Закрыта"
    def sort_key(deal):
        if deal.status == "Закрыта":
            return 1
        return 0
    deals.sort(key=sort_key)
    # --- NEW CODE END ---

    text = "💼 <b>Ваши сделки:</b>\n\n"
    builder = InlineKeyboardBuilder()

    for deal in deals:
        text += f"• <b>{deal.title}</b> — {deal.amount} ₽ [{deal.status}]\n"
        builder.button(text=f"🔄 {deal.id}", callback_data=f"deal_status_change:{deal.id}")
        builder.button(text=f"🗑 {deal.id}", callback_data=f"deal_del:{deal.id}")

    builder.adjust(2)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

# --- NEW CODE END ---


@router.callback_query(F.data.startswith("deal_status_change:"))
async def change_deal_status(callback: CallbackQuery):
    """
    Предлагает выбрать новый статус для сделки.
    """
    deal_id = int(callback.data.split(":")[1])
    builder = InlineKeyboardBuilder()
    for status in ["Открыта", "В процессе", "Закрыта"]:
        builder.button(text=status, callback_data=f"deal_set:{deal_id}:{status}")
    builder.adjust(1)
    await callback.message.answer("Выберите новый статус:", reply_markup=builder.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("deal_set:"))
async def set_deal_status(callback: CallbackQuery):
    """
    Сохраняет новый статус сделки.
    """
    _, deal_id, new_status = callback.data.split(":")
    deal_id = int(deal_id)
    async with async_session() as session:
        result = await session.execute(select(Deal).where(Deal.id == deal_id))
        deal = result.scalar_one_or_none()
        if deal:
            deal.status = new_status
            await session.commit()
            await callback.answer(f"Статус изменён на «{new_status}» ✅")
        else:
            await callback.answer("Сделка не найдена ❌", show_alert=True)


@router.callback_query(F.data.startswith("deal_del:"))
async def delete_deal(callback: CallbackQuery):
    """
    Удаляет сделку из базы данных.
    """
    deal_id = int(callback.data.split(":")[1])
    async with async_session() as session:
        await session.execute(delete(Deal).where(Deal.id == deal_id))
        await session.commit()
    await callback.answer("Сделка удалена 🗑")
    await callback.message.edit_text("Сделка удалена. Обновите список 📊")
