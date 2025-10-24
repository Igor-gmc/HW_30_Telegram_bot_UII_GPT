# --- NEW FILE: states/marketing_states.py ---

from aiogram.fsm.state import StatesGroup, State

class MarketingState(StatesGroup):
    waiting_for_problem = State()
