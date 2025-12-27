import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from expert.training import generate_training_plan
from keyboards import training_level_kb, training_goal_kb
from config import BOT_TOKEN
from keyboards import (
    main_menu,
    activity_kb,
    goal_kb,
    hormone_kb,
    cancel_kb,
    reminders_kb,
    technique_kb,
    technique_result_kb
)
from states import KBJUForm, TrainingForm, TechniqueForm
from expert.kbju import calculate_kbju
from llm.chat import ask_llm
from motivations import get_random_motivation

import json

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

user_reminders = {}  # user_id: True/False

#тут мотивашки
@dp.message(F.text == "Мотивашки ⚡️")
async def show_reminders_menu(message: Message):
    await message.answer(
        "Управление мотивационными уведомлениями:",
        reply_markup=reminders_kb()
    )

async def send_weekly_motivation(bot: Bot):
    """Периодическая задача для отправки мотивации раз в неделю"""
    await asyncio.sleep(5)  # небольшая задержка при старте
    while True:
        for user_id, enabled in user_reminders.items():
            if enabled:
                try:
                    await bot.send_message(user_id, get_random_motivation())
                except Exception:
                    pass  # если пользователь заблокировал бота, игнорируем
        await asyncio.sleep(7 * 24 * 60 * 60)  # 7 дней

#старт

@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я твой фитнес-тренер 👁👅👁\n\n"
        "Выбери, что хочешь сделать:",
        reply_markup=main_menu()
    )

#кнопочка отмены/главного меню
@dp.message(F.text == "❌ Отмена / Главное меню")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Хорошо! Возвращаемся в главное меню 🧚",
        reply_markup=main_menu()
    )

#КБЖУ!!

@dp.message(F.text == "Рассчитать КБЖУ 🥙")
async def kbju_start(message: Message, state: FSMContext):
    await state.set_state(KBJUForm.age)
    await message.answer("Введи свой возраст (целым числом, в годах) \n\n(Например: 20)", reply_markup=cancel_kb())

@dp.message(KBJUForm.age)
async def kbju_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть целым числом.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(KBJUForm.height)
    await message.answer("Введи рост (целым числом, в см) \n\nНапример: 170", reply_markup=cancel_kb())

@dp.message(KBJUForm.height)
async def kbju_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Рост должен быть целым числом.")
        return
    await state.update_data(height=int(message.text))
    await state.set_state(KBJUForm.weight)
    await message.answer("Введи вес (целым числом, в кг)\n\nНапример: 60", reply_markup=cancel_kb())

@dp.message(KBJUForm.weight)
async def kbju_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Вес должен быть целым числом.")
        return
    await state.update_data(weight=int(message.text))
    await state.set_state(KBJUForm.activity)
    await message.answer(
        "Выбери свой уровень физической активности\n\n\n"
        " 1️⃣ Небольшая активность (до 4000 шагов в день + до 2 тренировок в неделю)\n\n"
        " 2️⃣ Умеренная активность (до 10000 шагов в день + 2-4 тренировки в неделю)\n\n"
        " 3️⃣ Высокая активность (от 10000 шагов в день + от 3 тренировок, в том числе кардио/танцы/теннис и тд)\n\n"
        " 4️⃣ Очень высокая активность (от 15000 шагов в день + от 4х тренировок, в том числе кардио/танцы/теннис и тд, не сидячая работа)", reply_markup=activity_kb()
    )

@dp.message(KBJUForm.activity)
async def kbju_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text[0])
    except ValueError:
        await message.answer("Выбери вариант кнопкой.")
        return
    await state.update_data(activity=activity)
    await state.set_state(KBJUForm.goal)
    await message.answer("Отлично! Теперь выбери свою цель\n\n Если хочешь рассчитать дневную норму – выбирай рекомпозицию", reply_markup=goal_kb())

#ВЫБОР ЦЕЛИ ДЛЯ КБЖУ!!
@dp.message(KBJUForm.goal)
async def kbju_goal(message: Message, state: FSMContext):
    #это словарь соответствий текста кнопки - ключ цели д/calculate_kbju
    goal_map = {
        "Сушка": "lose",
        "Рекомпозиция": "recomp",
        "Массонабор": "bulk"
    }

    goal_key = goal_map.get(message.text)
    if not goal_key:
        await message.answer("Пожалуйста, выбери цель кнопкой.")
        return

    await state.update_data(goal=goal_key)
    await state.set_state(KBJUForm.hormones)
    await message.answer("Имеются ли у тебя гормональные нарушения?", reply_markup=hormone_kb())

#сам расчёт кбжу тут
@dp.message(KBJUForm.hormones)
async def kbju_result(message: Message, state: FSMContext):
    try:
        hormones = int(message.text[0])
    except ValueError:
        await message.answer("Выбери вариант кнопкой.")
        return

    data = await state.get_data()
    goal = data["goal"]

    #вызов calculate_kbju с корректным ключом
    result = calculate_kbju(
        age=data["age"],
        height=data["height"],
        weight=data["weight"],
        activity=data["activity"],
        hormones=hormones,
        goal=goal
    )

    if goal == "lose":
        text = (
            "Ура!! Держи свой расчёт КБЖУ на −10%:\n\n"
            f"Всего ккал на сушку: {result['cut_10']['calories']} ккал\n"
            f"Белков: {result['cut_10']['protein']} г\n"
            f"Жиров: {result['cut_10']['fats']} г\n"
            f"Углеводов: {result['cut_10']['carbs']} г\n\n"
            "Твой расчёт КБЖУ на −20%:\n\n"
            f"Всего ккал на сушку: {result['cut_20']['calories']} ккал\n"
            f"Белков: {result['cut_20']['protein']} г\n"
            f"Жиров: {result['cut_20']['fats']} г\n"
            f"Углеводов: {result['cut_20']['carbs']} г\n\n"
            "Подсказка: вне зависимости от твоего исходника, рекомендую начинать с дефицита -10%! Затем, если почувствуешь, что тебе это требуется и не вызовет дискомфорта, можешь переходить к дефициту 20%☀️"
        )
    elif goal == "recomp":
        r = result["maintenance"]
        text = (
            "Ура!! Держи свой расчёт КБЖУ на рекомпозицию (твоя дневная норма):\n\n"
            f"Всего ккал: {r['calories']} ккал\n"
            f"Белков: {r['protein']} г\n"
            f"Жиров: {r['fats']} г\n"
            f"Углеводов: {r['carbs']} г"
        )
    elif goal == "bulk":
        b = result["bulk"]
        text = (
            "Ура!! Держи свой расчёт КБЖУ на массонабор:\n\n"
            f"Всего ккал: {b['calories']} ккал\n"
            f"Белков: {b['protein']} г\n"
            f"Жиров: {b['fats']} г\n"
            f"Углеводов: {b['carbs']} г"
        )

    await message.answer(text, reply_markup=main_menu())
    await state.clear()


#ТРЕН ПЛАН!!!!

@dp.message(F.text == "Тренировочный план 🪄")
async def training_start(message: Message, state: FSMContext):
    await state.set_state(TrainingForm.level)
    await message.answer("Выбери свой уровень в силовых тренировках:", reply_markup=training_level_kb())

@dp.message(TrainingForm.level)
async def training_level(message: Message, state: FSMContext):
    text = message.text
    if "Новичок" in text:
        level = "beginner"
    elif "Средний" in text:
        level = "middle"
    else:
        level = "advanced"
    await state.update_data(level=level)
    await state.set_state(TrainingForm.goal)
    await message.answer("Выбери цель тренировок:", reply_markup=training_goal_kb())

MAX_MSG_LEN = 4000  #предел д/тгшки

async def send_long_message(message: Message, text: str):
    """Разбивает длинное сообщение на части и отправляет по очереди"""
    MAX_MSG_LEN = 4000
    for i in range(0, len(text), MAX_MSG_LEN):
        await message.answer(text[i:i+MAX_MSG_LEN])


MAX_MSG_LEN = 4000  #предел для тгшки

async def send_long_message(message: Message, text: str, reply_markup=None):
    """Разбивает длинное сообщение на части и отправляет по очереди"""
    for i in range(0, len(text), MAX_MSG_LEN):
        # Показываем клавиатуру только в последнем сообщении
        markup = reply_markup if i + MAX_MSG_LEN >= len(text) else None
        await message.answer(text[i:i+MAX_MSG_LEN], reply_markup=markup)


@dp.message(TrainingForm.goal)
async def training_goal(message: Message, state: FSMContext):
    from expert.training import generate_training_plan
    from llm.chat import ask_llm

    data = await state.get_data()
    level = data.get("level", "beginner")  # default beginner

    #словарь кнопок ключи целей
    button_map = {
        "Гипертрофия/раскачаться 💪": "bulk",
        "Похудеть 💨": "lose",
        "Фигура песочные часы ⌛️": "tone",
        "Здоровье ❤️": "health",
        "Домашние тренировки 🏠": "home"
    }

    goal_key = button_map.get(message.text)
    if not goal_key:
        await message.answer("Пожалуйста, выбери цель кнопкой.")
        return

    #генерит план
    plan = generate_training_plan(level, goal_key)

    #текст плана
    text = f"Супер! Держи свой тренировочный план 🫧🫧\n\nПомни, что перед каждой тренировкой важно делать суставную рамзинку на всё тело, а после рекомендую сделать хорошую заминку. Можно также закончить силовую тренировку комплексом на мышцы кора по желанию! В случае, если упражнений в списке слишком много, выбирай для тренировки те, что тебе нравятся больше всего <3\n\n"
    for day_index, split in enumerate(plan["split"]):
        exercises = plan["exercises"].get(split, [])
        text += f"День {day_index + 1} - {split}:\n"
        for ex in exercises:
            text += f"• {ex}\n"
        text += "\n"

    await send_long_message(message, text) #отправит план частями если что

    await message.answer( #показывает кнопку для техники
    "Хочешь узнать технику конкретного упражнения?",
    reply_markup=technique_kb()
)

    await state.clear()


    # Сбрасываем состояние
    await state.clear()



@dp.message(F.text == "ℹ️ Техника упражнения")
async def ask_exercise_name(message: Message, state: FSMContext):
    await state.set_state(TechniqueForm.exercise_name)
    await message.answer(
        "Напиши название упражнения\n\nНапример: ягодичный мост в тренажёре, приседания",
        reply_markup=cancel_kb()
    )

def find_exercise(name: str):
    with open("data/exercises.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    name_lower = name.lower()
    for group in data.values():
        for ex in group:
            if ex["name"].lower() == name_lower:
                return ex
    return None

@dp.message(TechniqueForm.exercise_name)
async def show_technique(message: Message, state: FSMContext):
    ex = find_exercise(message.text)

    if ex:
        text = (
            f"{ex['name']}\n\n"
            f"{ex['base_technique']}\n\n"
            f"Оборудование: {ex['equipment']}"
        )
    else:
        # fallback на ИИ
        text = ask_llm(
            f"Объясни технику упражнения '{message.text}', выполняемого в тренажёрном зале с весом или без веса, простым и безопасным языком"
        )

    await message.answer(
        text,
        reply_markup=technique_result_kb()
    )
    await state.clear()

#ОБРАБОТЧИК КНОПКИ «ДРУГОЕ УПР»!
@dp.message(F.text == "🔁 Другое упражнение")
async def another_exercise(message: Message, state: FSMContext):
    await state.set_state(TechniqueForm.exercise_name)
    await message.answer(
        "Напиши название упражнения:",
        reply_markup=cancel_kb()
    )
@dp.message(F.text == "🏠 Главное меню")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Ты в главном меню 🏠",
        reply_markup=main_menu()
    )



#ЛЛМ 

@dp.message(F.text == "Задать вопрос 💬")
async def chat_start(message: Message):
    await message.answer(
        "Задай любой вопрос про тренировки, технику выполнения упражнений или, например, подбор рабочего веса!",
                         reply_markup=cancel_kb()
    )

@dp.message()
async def free_chat(message: Message):
    if message.text == "❌ Отмена / Главное меню":
        return
    answer = ask_llm(message.text)
    await message.answer(answer, reply_markup=main_menu())

#напоминалки!

@dp.callback_query(lambda c: c.data in ["reminders_on", "reminders_off"])
async def reminders_toggle(callback: CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "reminders_on":
        user_reminders[user_id] = True
        await callback.message.answer("✅ Мотивационные напоминания включены!")
    else:
        user_reminders[user_id] = False
        await callback.message.answer("❌ Мотивационные напоминания выключены!")
    await callback.answer()

async def main():
    asyncio.create_task(send_weekly_motivation(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
