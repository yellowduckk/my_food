import json
from pathlib import Path

from my_food_json_files.dish_classes import Dish, Ingredient, Preference, FoodType, Device


def load_ingredients() -> Ingredient:
    """
    :return: обернутые в класс ингредиенты
    """
    with open(Path(Path(__file__).parent, "ingredients.json"), "r", encoding="utf-8") as file:
        ingredients = json.load(file)
    result_ingredient = [Ingredient(**ingredient) for ingredient in ingredients["ingredients"]]

    return result_ingredient


def load_preferences():
    with open(Path(Path(__file__).parent, "preferences.json"), "r", encoding="utf-8") as file:
        preferences = json.load(file)

    return [Preference(preference) for preference in preferences["preferences"]]


def load_food_types():
    with open(Path(Path(__file__).parent, "food_types.json"), "r", encoding="utf-8") as file:
        food_types = json.load(file)

    return [FoodType(food_type) for food_type in food_types["food_types"]]


def load_food_devices():
    with open(Path(Path(__file__).parent, "food_devices.json"), "r", encoding="utf-8") as file:
        devices = json.load(file)

    return [Device(device) for device in devices["food_devices"]]

# print(load_ingredients())
# print(load_preferences())
# print(load_food_types())
# print(load_food_devices())
