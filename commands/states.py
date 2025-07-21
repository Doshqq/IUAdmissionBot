from aiogram.fsm.state import StatesGroup, State

class AddingState(StatesGroup):
    awaiting_document = State()

class CategoryState(StatesGroup):
    awaiting_name = State()

class ApplicationState(StatesGroup):
    choosing_direction = State()
    collecting_certificate = State()
    collecting_photo = State()
