from aiogram.fsm.state import StatesGroup, State

class DealAddState(StatesGroup):
    """
    Состояния мастера добавления сделки.
    """
    waiting_for_title = State()
    waiting_for_amount = State()
    waiting_for_status = State()
