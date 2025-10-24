from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Тексты кнопок выносим в константы — чтобы не ловить опечатки в хендлерах
BTN_ADD_TASK = "➕ Добавить задачу"
BTN_VIEW_TASKS = "📋 Просмотреть задачи"
BTN_ADD_DEAL = "💼 Добавить сделку"
BTN_VIEW_DEALS = "📊 Просмотреть сделки"
BTN_GET_MARKETING = "💡 Совет по маркетингу"
BTN_GET_MOTIVATION = "⚡️ Мотивация"

def main_menu() -> ReplyKeyboardMarkup:
    """
    Возвращает основное меню бота с кнопками.
    Клавиатура Reply — остаётся на экране до следующей смены.
    """
    kb = [
        [KeyboardButton(text=BTN_ADD_TASK), KeyboardButton(text=BTN_VIEW_TASKS)],
        [KeyboardButton(text=BTN_ADD_DEAL), KeyboardButton(text=BTN_VIEW_DEALS)],
        [KeyboardButton(text=BTN_GET_MARKETING), KeyboardButton(text=BTN_GET_MOTIVATION)],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие…"
    )