import json
from pathlib import Path

from my_food_randomizer.dish_classes import Dish


def load_dishes():
    with open(Path(Path(__file__).parent, "data_of_dishes.json"), "r", encoding="utf-8") as f:
        dishes_data = json.load(f)

    return [Dish(**dish) for dish in dishes_data["dishes"]]
