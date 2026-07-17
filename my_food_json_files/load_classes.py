import json
from pathlib import Path

from my_food_json_files.dish_classes import Dish, Ingredient, Preference, FoodType, Device


def load_ingredients() -> list[Ingredient]:
    """
    :return: обернутые в класс ингредиенты
    """
    with open(Path(Path(__file__).parent, "ingredients.json"), "r", encoding="utf-8") as file:
        ingredients = json.load(file)
    result_ingredient = [Ingredient(**ingredient) for ingredient in ingredients["ingredients"]]

    return result_ingredient

def load_preferences() -> list[Preference]:
    """
    :return: обёрнутые ы класс сезонные предпочтения
    """
    with open(Path(Path(__file__).parent, "preferences.json"), "r", encoding="utf-8") as file:
        preferences = json.load(file)
    result_preferences = [Preference(preference) for preference in preferences["preferences"]]

    return result_preferences

def load_food_types() -> list[FoodType]:
    """
    :return: обёрнутые в класс типы еды
    """
    with open(Path(Path(__file__).parent, "food_types.json"), "r", encoding="utf-8") as file:
        food_types = json.load(file)
    result_food_types = [FoodType(food_type) for food_type in food_types["food_types"]]

    return result_food_types

def load_food_devices() -> list[Device]:
    """
    :return: обёрнутые в класс девайсы для приготовления еды
    """
    with open(Path(Path(__file__).parent, "food_devices.json"), "r", encoding="utf-8") as file:
        devices = json.load(file)
    result_devices = [Device(device) for device in devices["food_devices"]]

    return result_devices

def load_dish():
    """
    :return: обёрнутые в класс блюда
    """
    with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
        dishes = json.load(file)
    result_dish = [Dish(**dish) for dish in dishes["dishes"]]

    return result_dish

# print(load_ingredients())
# print(load_preferences())
# print(load_food_types())
# print(load_food_devices())
