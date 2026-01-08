from aiogram.fsm.state import State, StatesGroup

class AdminAuth(StatesGroup):
    waiting_for_password = State()
