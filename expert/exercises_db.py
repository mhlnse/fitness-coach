import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "exercises.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    EXERCISES = json.load(f)

def get_exercises(level: str, goal: str, place: str = "gym"):
    result = []

    for muscle, exercises in EXERCISES.items():
        for ex in exercises:
            if (
                level in ex["level"]
                and goal in ex["goals"]
                and place in ex["place"]
            ):
                result.append(ex)

    return result
