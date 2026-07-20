from random import random
import json
from pathlib import Path
from typing import List
from load_classes import dish_loader
from dish_classes import *


class AddDish:
    def __init__(self, dishes: List[Dish], ingredients: List[Ingredient], preferences: List[Preference], food_types: List[FoodType], devices: List[Device]):
        self.dishes = dishes
        self.ingredients = ingredients
        self.preferences = preferences
        self.food_types = food_types
        self.devices = devices

    def add_d(self, name: str, food_type: str, new_preferences: list[str], food_device: str, new_ingredients: dict[str: int], cooking_time: int, eating_time: int):
        dishes_names = [dish.name for dish in self.dishes]
        ingredients_names = [ingredient.name for ingredient in self.ingredients]
        preferences_names = [preference.name for preference in self.preferences]
        food_types_names = [food_type.name for food_type in self.food_types]
        devices_names = [device.name for device in self.devices]
        print(dishes_names)
        dish_dict = {}
        dish_dict["id"] = len(dishes_names) + 1
        if name in dishes_names:
            print("Такое блюдо уже есть")
            return None
        else:
            dish_dict["name"] = name
            if food_type not in food_types_names:
                print("Такого типа блюд нет")
            dish_dict["food_type"] = food_type
            dish_dict["preferences"] = []
            for preference in new_preferences:
                if preference in preferences_names:
                    dish_dict["preferences"].append(preference)
            if food_device not in devices_names:
                print("Такого девайса нет")
            dish_dict["food_device"] = food_device
            dish_dict["ingredients"] = {}
            for ingredient in new_ingredients.keys():
                if ingredient in ingredients_names:
                    dish_dict["ingredients"][ingredient] = new_ingredients[ingredient]
                    # unit = input("Введите единицу измерения количества ингредиента: ")
                    # Ingredient(**{"name": ingredient, "unit": unit})
            dish_dict["cooking_time"] = cooking_time
            dish_dict["eating_time"] = eating_time
        with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
            dishes_json = json.load(file)
        with open(Path(Path(__file__).parent, "dishes.json"), "r+", encoding="utf-8") as file:
            dishes_json["dishes"].append(dish_dict)
            json.dump(dishes_json, file, ensure_ascii=False, indent=4)
        for key in dish_dict.keys():
            print(f"{key}: {dish_dict[key]}")

        # while True:
        #     dish_dict = {}
        #     dish_dict["id"] = len(dishes_names) + 1
        #     name = input("Введите название блюда: ")
        #     if name in dishes_names:
        #         print("Такое блюдо уже есть")
        #         continue
        #     else:
        #         dish_dict["name"] = name
        #     food_type = input("Введите тип блюда: ")
        #     if food_type not in food_types_names:
        #         print("Такого блюда нет")
        #         continue
        #         # FoodType(food_type)
        #     dish_dict["food_type"] = food_type
        #     dish_dict["preferences"] = []
        #     while True:
        #         preference = input("Введите новое предпочтение: ")
        #         if preference == "":
        #             break
        #         elif preference in preferences_names:
        #             dish_dict["preferences"].append(preference)
        #         else:
        #             print("Нельзя ввести новое предпочтение")
        #     food_device = input("Введите название девайса, на котором можно приготовить это блюдо: ")
        #     if food_device not in devices_names:
        #         print("Такого девайса нет")
        #         continue
        #     dish_dict["food_device"] = food_device
        #     dish_dict["ingredients"] = {}
        #     while True:
        #         ingredient = input("Введите ингредиент: ")
        #         if ingredient == "":
        #             break
        #         elif ingredient not in ingredients_names:
        #             # unit = input("Введите единицу измерения количества ингредиента: ")
        #             # Ingredient(**{"name": ingredient, "unit": unit})
        #             print("Нельзя ввести данный ингредиент")
        #             continue
        #         quantity = int(input(f"Введите объём/вес/количество {ingredient}: "))
        #         dish_dict["ingredients"][ingredient] = quantity
        #     dish_dict["cooking_time"] = int(input("Введите время приготовления блюда: "))
        #     dish_dict["eating_time"] = int(input("Введите время, за которое это блюдо будет съедено: "))
        #     break
        # with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
        #     dishes_json = json.load(file)
        # with open(Path(Path(__file__).parent, "dishes.json"), "r+", encoding="utf-8") as file:
        #     dishes_json["dishes"].append(dish_dict)
        #     json.dump(dishes_json, file, ensure_ascii=False, indent=4)
        # for key in dish_dict.keys():
        #     print(f"{key}: {dish_dict[key]}")

d_l = dish_loader()
AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices()).add_d("Святослав", "салат", ["лето", "зима"],
                                                                                                                               "плита", {"булгур": 1, "помидор": 1},
                                                                                                                               1000, 1)


# {
#     "dishes": []
# }