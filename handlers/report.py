# --- NEW FILE: handlers/report.py ---

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from database.db import async_session
from database.models import User, Task
from handlers.deals import Deal  # используем ту же модель
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("report"))
async def send_report(message: Message):
    """
    Отчёт за текущую сессию:
    - количество завершённых задач;
    - количество закрытых сделок и их общая сумма.
    """
    tg_user = message.from_user

    async with async_session() as session:
        # 1️⃣ Завершённые задачи
        result_tasks = await session.execute(
            select(func.count(Task.id)).join(User).where(
                User.tg_id == tg_user.id, Task.status == "Выполнена"
            )
        )
        completed_tasks = result_tasks.scalar() or 0

        # 2️⃣ Закрытые сделки
        result_deals = await session.execute(
            select(
                func.count(Deal.id),
                func.coalesce(func.sum(Deal.amount), 0)
            ).join(User).where(User.tg_id == tg_user.id, Deal.status == "Закрыта")
        )
        deals_count, deals_sum = result_deals.one()

    report_text = (
        f"📊 <b>Отчёт на {datetime.now():%d.%m.%Y %H:%M}</b>\n\n"
        f"✅ Завершено задач: {completed_tasks}\n"
        f"💼 Закрыто сделок: {deals_count}\n"
        f"💰 Общая сумма: {deals_sum} ₽"
    )

    await message.answer(report_text, parse_mode="HTML")
    logger.info("Отчёт отправлен пользователю %s", tg_user.id)
