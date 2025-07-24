from aiogram.fsm.state import StatesGroup, State


# Application
class AddingState(StatesGroup):
    awaiting_document = State()

class CategoryState(StatesGroup):
    awaiting_name = State()

class ApplicationState(StatesGroup):
    choosing_direction = State()
    collecting_certificate = State()
    collecting_photo = State()

# Admission ranking
class FindMeState(StatesGroup):
    education_level = State()
    enrollment_basis = State()
    enrollment_category = State()
    program = State()
    awaiting_id = State()
    searching = State()

# Support
class SupportState(StatesGroup):
    waiting_for_question = State()
    waiting_for_reply = State()
