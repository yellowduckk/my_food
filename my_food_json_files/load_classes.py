import json
from pathlib import Path

from my_food_json_files.dish_classes import Dish, Ingredient, Preference, FoodType, Device, Unit

from dataclasses import dataclass
from frozendict import frozendict

class DishLoader:
    def __init__(self):
        self.preferences = []
        self.food_types = []
        self.devices = []
        self.ingredients = []
        self.units = []

    # def list_to_tuple(self, ingredients):
    #     for ingredient in ingredients:
    #         ingredient.unit =


    def find_with_name(self, massive: list[FoodType|Device|Preference|Ingredient|Unit], name: str) -> FoodType|Device|Preference|Ingredient|Unit|None:
        """
        :param massive: массив, где надо найти объект с соответсвующим наименованием
        :param name: наименование
        :return: объект с соответсвтующим наименованием или None
        """
        for element in massive:
            if element.name == name:
                return element
        return None

    def load_units(self) -> list[Unit]:
        """
        :return: обёрнутые в класс единицы измерения
        """
        with open(Path(Path(__file__).parent, "units.json"), "r", encoding="utf-8") as file:
            units = json.load(file)
        for unit in units["units"]:
            unit["alternatives"] = frozendict(unit["alternatives"])
        result_units = [Unit(**unit) for unit in units["units"]]
        self.units = result_units

        return result_units

    def load_ingredients(self) -> list[Ingredient]:
        """
        :return: обёрнутые в класс ингредиенты
        """
        self.load_units()
        with open(Path(Path(__file__).parent, "ingredients.json"), "r", encoding="utf-8") as file:
            ingredients = json.load(file)
        result_ingredient = []
        for ingredient in ingredients["ingredients"]:
            for index in range(0, len(ingredient["unit"])):
                ingredient["unit"][index] = self.find_with_name(self.units, ingredient["unit"][index])
            ingredient["unit"] = tuple(ingredient["unit"])
            result_ingredient.append(Ingredient(**ingredient))
        self.ingredients = result_ingredient

        return result_ingredient

    def load_preferences(self) -> list[Preference]:
        """
        :return: обёрнутые ы класс сезонные предпочтения
        """
        with open(Path(Path(__file__).parent, "preferences.json"), "r", encoding="utf-8") as file:
            preferences = json.load(file)
        result_preferences = [Preference(preference) for preference in preferences["preferences"]]
        self.preferences = result_preferences

        return result_preferences

    def load_food_types(self) -> list[FoodType]:
        """
        :return: обёрнутые в класс типы еды
        """
        with open(Path(Path(__file__).parent, "food_types.json"), "r", encoding="utf-8") as file:
            food_types = json.load(file)
        result_food_types = [FoodType(food_type) for food_type in food_types["food_types"]]
        self.food_types = result_food_types

        return result_food_types

    def load_food_devices(self) -> list[Device]:
        """
        :return: обёрнутые в класс девайсы для приготовления еды
        """
        with open(Path(Path(__file__).parent, "food_devices.json"), "r", encoding="utf-8") as file:
            devices = json.load(file)
        result_devices = [Device(device) for device in devices["food_devices"]]
        self.devices = result_devices

        return result_devices

    def load_dish(self) -> list[Dish]:
        """
        :return: обёрнутые в класс блюда c объектами вместо имён в параметрах food_type, preferences, food_device, ingredients
        """
        self.load_food_types()
        self.load_food_devices()
        self.load_preferences()
        self.load_ingredients()
        with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
            dishes = json.load(file)
        result_dish = []
        for dish in dishes["dishes"]:
            dish["food_type"] = self.find_with_name(self.food_types, dish["food_type"])
            for index in range(0, len(dish["preferences"])):
                dish["preferences"][index] = self.find_with_name(self.preferences, dish["preferences"][index])
            dish["food_device"] = self.find_with_name(self.devices, dish["food_device"])
            dish_ingredients_keys = list(dish["ingredients"].keys())
            dict_ingredients = {}
            for index in range(0, len(dish_ingredients_keys)):
                full_index = dish_ingredients_keys[index]
                print(full_index)
                ingredient = self.find_with_name(self.ingredients, full_index)
                print(ingredient)
                dict_ingredients[ingredient] = (dish["ingredients"][full_index][0], self.find_with_name(self.units, dish["ingredients"][full_index][1]))
            dish["ingredients"] = dict_ingredients
            result_dish.append(Dish(**dish))
            # print(result_dish)
        return result_dish
