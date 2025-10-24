from aiogram.fsm.state import StatesGroup, State

class TaskAddState(StatesGroup):
    """
    Состояния мастера добавления задачи.
    """
    waiting_for_title = State()
    waiting_for_time = State()
