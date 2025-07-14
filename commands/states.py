from aiogram.fsm.state import StatesGroup, State

class AddingState(StatesGroup):
    awaiting_document = State()

class CategoryState(StatesGroup):
    awaiting_name = State()
