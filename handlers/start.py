import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.reply import main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Приветствие и выдача основного меню.
    """
    user = message.from_user
    logger.info("User %s (%s) invoked /start", user.id, user.username)
    await message.answer(
        "Привет! Я помощник менеджера и маркетолога.\nВыберите действие 👇",
        reply_markup=main_menu()
    )
