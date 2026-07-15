from random import random
import json
from pathlib import Path
from typing import List
from my_food_json_files.dish_classes import Dish, Ingredient, Preference, FoodType, Device

class AddDish:
    def __init__(self, dishes: List[Dish], ingredients: List[Ingredient], preferences: List[Preference], food_types: List[FoodType], devices: List[Device]):
        self.dishes = dishes
        self.ingredients = ingredients
        self.preferences = preferences
        self.food_types = food_types
        self.devices = devices

    def generate_names(self, massive):
        for element in massive:
            yield element.name


    def add_dish(self):
        dishes_names = [self.generate_names(self.dishes)]
        ingredients_names = [self.generate_names(self.ingredients)]
        preferences_names = [self.generate_names(self.preferences)]
        food_types_names = [self.generate_names(self.food_types)]
        devices_names = [self.generate_names(self.devices)]
        dish_dict = {}

        while True:
            dish_dict = {}
            dish_dict["id"] = len(dishes_names) + 1
            name = input("Введите название блюда: ")
            if name in dishes_names:
                print("Такое блюдо уже есть")
                continue
            else:
                dish_dict["name"] = name
            food_type = input("Введите тип блюда: ")
            if food_type not in food_types_names:
                FoodType(food_type)
            dish_dict["food_type"] = self.food_types[food_types_names.index(food_type)]
            dish_dict["preferences"] = []
            while True:
                preference = input("Введите новое предпочтение: ")
                if preference == "":
                    break
                elif preference in preferences_names:
                    dish_dict["preferences"].append(preference)
                else:
                    print("Нельзя ввести новое предпочтение")
            food_device = input("Введите название девайса, на котором можно приготовить это блюдо: ")
            if food_device not in devices_names:
                Device(food_device)
            dish_dict["food_device"] = self.devices[devices_names.index(food_device)]
            dish_dict["ingredients"] = {}
            while True:
                ingredient = input("Введите ингридиент: ")
                if ingredient == "":
                    break
                elif ingredient not in ingredients_names:
                    unit = input("Введите еденицу измерения количества ингридиента: ")
                    Ingredient(**{"name": ingredient, "unit": unit})
                quantity = int(input(f"Введите объём/вес/количество {ingredient}: "))
                dish_dict["ingredients"][self.ingredients[ingredients_names.index(ingredient)]] = quantity
            dish_dict["cooking_time"] = int(input("Введите время приготовления блюда: "))
            dish_dict["eating_time"] = int(input("Введите время, за которое это блюдо будет съедено: "))
            break
        with open(Path(Path(__file__).parent, "ingredients.json"), "r", encoding="utf-8") as file:
            dishes_json = json.load(file)
            dishes_json.append(dish_dict)
            json.dump(dishes_json, file, ensure_ascii=False, indent=4)
        print(*dish_dict, sep="\n")

AddDish(Dish, Ingredient, Preference, FoodType, Device).add_dish()




