# --- NEW FILE: handlers/marketing.py ---

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.marketing_states import MarketingState
from services.chatgpt import get_marketing_advice
from keyboards.reply import BTN_GET_MARKETING

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == BTN_GET_MARKETING)
@router.message(Command("marketing"))
async def ask_marketing_question(message: Message, state: FSMContext):
    """
    Запускает процесс получения совета: запрашиваем у пользователя проблему.
    """
    await state.set_state(MarketingState.waiting_for_problem)
    await message.answer("Опиши кратко маркетинговую задачу или проблему, например:\n«Как увеличить продажи летом?»")

@router.message(MarketingState.waiting_for_problem)
async def send_marketing_advice(message: Message, state: FSMContext):
    """
    Получает запрос пользователя, отправляет его в ChatGPT и возвращает совет.
    """
    problem = message.text.strip()
    await message.answer("⏳ Думаю над советом...")
    advice = await get_marketing_advice(problem)
    await state.clear()
    await message.answer(f"💡 Совет по маркетингу:\n\n{advice}")
