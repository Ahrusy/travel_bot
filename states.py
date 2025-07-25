from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_city = State()
    waiting_for_translate = State()
    waiting_for_country = State()
