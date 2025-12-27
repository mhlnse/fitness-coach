import json
import random
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    EXERCISES = json.load(f)

def get_exercises_for_split(split, level, goal, exercises_json):
    #возвращает список упражнений для конкретного сплита, уровня и цели
    mapping = {
        "Full Body": [
            "chest", "back",
            "biceps", "triceps",
            "legs", "glutes", "core"
        ],

        "Upper": [
            "chest",
            "biceps"
        ],

        "Back": [
            "back",
            "triceps"
        ],

        "Lower": [
            "legs",
            "glutes"
        ],

        "Core": [
            "core"
        ]
    }
    result = []
    for group in mapping.get(split, []):
        for ex in exercises_json.get(group, []):
            if level in ex["level"] and goal in ex["goals"]:
                result.append(ex["name"])
    return result

def generate_training_plan(level: str, goal: str):
    plan = {"days": 0, "split": [], "exercises": {}}

    if goal == "tone":  # песочные часы
        plan["split"] = ["Lower", "Back", "Upper"]
        plan["days"] = len(plan["split"])
    elif goal == "lose":
        plan["split"] = ["Full Body", "Back", "Lower"]
        plan["days"] = len(plan["split"])
    elif goal == "bulk":
        plan["split"] = ["Upper", "Lower", "Back"]
        plan["days"] = len(plan["split"])
    elif goal == "health":
        plan["split"] = ["Full Body", "Upper", "Back", "Lower"]
        plan["days"] = len(plan["split"])
    elif goal == "home":
        plan["split"] = ["Full Body", "Back", "Lower"]
        plan["days"] = len(plan["split"])
    else:
        plan["split"] = ["Full Body"]
        plan["days"] = 1

    #генерация упражнений д/аждого сплита
    for split in set(plan["split"]):
        plan["exercises"][split] = get_exercises_for_split(split, level, goal, EXERCISES)

    return plan
