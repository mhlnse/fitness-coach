from aiogram.fsm.state import StatesGroup, State

class KBJUForm(StatesGroup):
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()
    hormones = State()

class TrainingForm(StatesGroup):
    level = State()
    age = State()
    height = State()
    weight = State()
    goal = State()

class TechniqueForm(StatesGroup):
    exercise_name = State()