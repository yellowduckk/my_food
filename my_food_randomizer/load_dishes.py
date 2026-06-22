import json
from pathlib import Path

from my_food_randomizer.dish_classes import Dish


def load_dish():
    with open(Path(Path(__file__).parent, "data_of_dishes.json"), "r", encoding="utf-8") as f:
        dishes_data = json.load(f)
# Создаёт объект из json файла data_of_dishes

    return [Dish(**dish) for dish in dishes_data["dishes"]]
# Возвращает массив классов Dish с аргументами из файла