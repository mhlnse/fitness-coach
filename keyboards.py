from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рассчитать КБЖУ 🥙")],
            [KeyboardButton(text="Тренировочный план 🪄")],
            [KeyboardButton(text="Задать вопрос 💬")],
            [KeyboardButton(text="Мотивашки ⚡️")]
        ],
        resize_keyboard=True
    )

def activity_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1️⃣ Небольшая активность")],
            [KeyboardButton(text="2️⃣ Умеренная активность")],
            [KeyboardButton(text="3️⃣ Высокая активность")],
            [KeyboardButton(text="4️⃣ Очень высокая активность")]
        ],
        resize_keyboard=True
    )

def goal_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сушка")],
            [KeyboardButton(text="Рекомпозиция")],
            [KeyboardButton(text="Массонабор")]
        ],
        resize_keyboard=True
    )

def hormone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1️⃣ Нет/не знаю")],
            [KeyboardButton(text="2️⃣ Гипотиреоз")],
            [KeyboardButton(text="3️⃣ Инсулинорезистентность")],
            [KeyboardButton(text="4️⃣ Дефицит половых гормонов")],
            [KeyboardButton(text="5️⃣ Эндокринные нарушения")]
        ],
        resize_keyboard=True
    )

def training_level_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новичок/недавно начал 💚")],
            [KeyboardButton(text="Средний (тренируюсь до года) 🩵")],
            [KeyboardButton(text="Продвинутый (1+ год тренировок) 💜")]
        ],
        resize_keyboard=True
    )

def training_goal_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Гипертрофия/раскачаться 💪")],
            [KeyboardButton(text="Похудеть 💨")],
            [KeyboardButton(text="Фигура песочные часы ⌛️")],
            [KeyboardButton(text="Здоровье ❤️")],
            [KeyboardButton(text="Домашние тренировки 🏠")]
        ],
        resize_keyboard=True
    )

def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена / Главное меню")]
        ],
        resize_keyboard=True
    )

def reminders_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Включить мотивацию ✅",
                    callback_data="reminders_on"
                ),
                InlineKeyboardButton(
                    text="Выключить мотивацию ❌",
                    callback_data="reminders_off"
                )
            ]
        ]
    )

def technique_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Техника упражнения")],
            [KeyboardButton(text="❌ Отмена / Главное меню")]
        ],
        resize_keyboard=True
    )

def technique_result_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔁 Другое упражнение")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )