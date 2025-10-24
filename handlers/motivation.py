# --- NEW FILE: handlers/motivation.py ---

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from services.chatgpt import get_motivation_phrase
from keyboards.reply import BTN_GET_MOTIVATION

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == BTN_GET_MOTIVATION)
@router.message(Command("motivation"))
async def send_motivation(message: Message):
    """
    Генерирует и отправляет мотивационную фразу через ChatGPT.
    """
    await message.answer("💭 Думаю над мотивацией...")
    phrase = await get_motivation_phrase()
    await message.answer(f"⚡️ {phrase}")
