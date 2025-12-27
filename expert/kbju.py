# expert/kbju.py

ACTIVITY = {
    1: 1.3,
    2: 1.5,
    3: 1.7,
    4: 1.9
}

HORMONES = {
    1: 1.0,
    2: 0.90,
    3: 0.83,
    4: 0.90,
    5: 0.85
}


def calculate_kbju(
    age: int,
    height: int,
    weight: int,
    activity: int,
    hormones: int,
    goal: str
):
    #BMR – базовый метаболизм (Миффлин-Сан Жеор)
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
    maintenance = bmr * ACTIVITY[activity] * HORMONES[hormones]

    protein = round(1.8 * weight)
    fats = round(1.0 * weight)

    def calc(carbs_calories):
        return round((carbs_calories - protein * 4 - fats * 9) / 4)

    if goal == "lose":
        cut_10 = maintenance * 0.90
        cut_20 = maintenance * 0.80

        return {
            "cut_10": {
                "calories": round(cut_10),
                "protein": protein,
                "fats": fats,
                "carbs": calc(cut_10)
            },
            "cut_20": {
                "calories": round(cut_20),
                "protein": protein,
                "fats": fats,
                "carbs": calc(cut_20)
            }
        }

    if goal == "recomp":
        return {
            "maintenance": {
                "calories": round(maintenance),
                "protein": protein,
                "fats": fats,
                "carbs": calc(maintenance)
            }
        }

    if goal == "bulk":
        bulk = maintenance * 1.12  # +12 проц — оптимально

        return {
            "bulk": {
                "calories": round(bulk),
                "protein": protein,
                "fats": fats,
                "carbs": calc(bulk)
            }
        }

    raise ValueError("Неизвестная цель")