import json
from pathlib import Path
from typing import List
from my_food_json_files.load_classes import DishLoader
from my_food_json_files.dish_classes import *


class AddDish:
    def __init__(self, dishes: List[Dish], ingredients: List[Ingredient], preferences: List[Preference], food_types: List[FoodType], devices: List[Device], units: List[Unit]):
        self.dishes = dishes
        self.ingredients = ingredients
        self.preferences = preferences
        self.food_types = food_types
        self.devices = devices
        self.units = units

    def del_d(self, name: str) -> None:
        """
        :param name: название блюда, которое нужно удалить
        :return: возвращает None, если блюда с таким названием нет в базе данных, иначе ничего не возвращает (но удаляет блюдо с таким именем из базы данных)
        """
        name = name.lower()
        dishes_names = [dish.name for dish in self.dishes]
        if name in dishes_names:
            with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
                dishes_json = json.load(file)
            with open(Path(Path(__file__).parent, "dishes.json"), "w", encoding="utf-8") as file:
                dish_ind_0 = dishes_names.index(name)
                dishes_json["dishes"].pop(dish_ind_0)
                if len(dishes_names) > 1:
                    for dish_ind in range(dish_ind_0, len(self.dishes)):
                        dishes_json["dishes"][dish_ind - 1]["id"] = dish_ind
                json.dump(dishes_json, file, ensure_ascii=False, indent=4)
        else:
            return None


    def add_d(self, name: str, food_type: str, new_preferences: list[str], food_device: str, new_ingredients: dict[str: int], cooking_time: int, eating_time: int) -> None:
        """
        :param name: название нового блюда
        :param food_type: тип нового блюда
        :param new_preferences: массив предпочтений (времена года)
        :param food_device: девайс, с помощью которого нужно готовить новое блюдо
        :param new_ingredients: словарь ингредиентов, из которых нужно готовить новое блюда
        :param cooking_time: время, за которое готовится новое блюдо
        :param eating_time: время, за которое можно съесть данное блюдо
        :return: возвращает None, если один из параметров не соответсвтует заданным условиям (если нет, то ничего не возвращает, но записывает новое блюдо в базу данных)
        """
        dishes_names = [dish.name for dish in self.dishes]
        ingredients_names = [ingredient.name for ingredient in self.ingredients]
        preferences_names = [preference.name for preference in self.preferences]
        food_types_names = [food_type.name for food_type in self.food_types]
        devices_names = [device.name for device in self.devices]
        dish_dict = {}
        dish_dict["id"] = len(dishes_names) + 1
        name = name.lower()
        food_type = food_type.lower()
        new_preferences = list(map(lambda pref: pref.lower(), new_preferences))
        food_device = food_device.lower()
        busted_ings = []
        for ing in new_ingredients.keys():
            if ing != ing.lower():
                busted_ings.append(ing)
        for ing in busted_ings:
            new_ingredients[ing.lower()] = new_ingredients[ing]
            new_ingredients.pop(ing)
        if name.lower() in dishes_names:
            print("Такое блюдо уже есть")
            return None
        else:
            dish_dict["name"] = name
            if food_type.lower() not in food_types_names:
                print("Такого типа блюд нет")
                return None
            dish_dict["food_type"] = food_type
            dish_dict["preferences"] = []
            for preference in new_preferences:
                if preference.lower() in preferences_names:
                    dish_dict["preferences"].append(preference)
                else:
                    print("Такого времени года нет")
                    return None
            if food_device.lower() not in devices_names:
                print("Такого девайса нет")
                return None
            dish_dict["food_device"] = food_device
            dish_dict["ingredients"] = {}
            for ingredient in new_ingredients.keys():
                if ingredient in ingredients_names:
                    dish_dict["ingredients"][ingredient] = new_ingredients[ingredient]
                else:
                    print("Такого ингредиента нет")
                    return None
            if  isinstance(eating_time, int) and cooking_time > 0 and cooking_time < 6:
                dish_dict["cooking_time"] = cooking_time
            else:
                print("Блюда столько не готовятся")
                return None
            if isinstance(eating_time, int) and eating_time > 0 and eating_time < 6:
                dish_dict["eating_time"] = eating_time
            else:
                print("Блюда столько не едятся")
                return None
        with open(Path(Path(__file__).parent, "dishes.json"), "r", encoding="utf-8") as file:
            dishes_json = json.load(file)
        with open(Path(Path(__file__).parent, "dishes.json"), "w", encoding="utf-8") as file:
            dishes_json["dishes"].append(dish_dict)
            json.dump(dishes_json, file, ensure_ascii=False, indent=4)
        for key in dish_dict.keys():
            print(f"{key}: {dish_dict[key]}")

# d_l = dish_loader()
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.add_d("СвятоСлав1", "САлат",["лЕТо", "зима"],"пЛита", {"булгур": 1, "поМидор": 1},1, 1)
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.add_d("СвятоСлав2", "САлат",["лЕТо", "зима"],"пЛита", {"булгур": 1, "поМидор": 1},1, 1)
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.add_d("СвятоСлав3", "САлат",["лЕТо", "зима"],"пЛита", {"булгур": 1, "поМидор": 1},1, 1)
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.add_d("СвятоСлав4", "САлат",["лЕТо", "зима"],"пЛита", {"булгур": 1, "поМидор": 1},1, 1)
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.add_d("СвятоСлав5", "САлат",["лЕТо", "зима"],"пЛита", {"булгур": 1, "поМидор": 1},1, 1)
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.del_d("СвятоСлав1")
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.del_d("СвятоСлав3")
# a_d = AddDish(d_l.load_dish(), d_l.load_ingredients(), d_l.load_preferences(), d_l.load_food_types(), d_l.load_food_devices())
# a_d.del_d("СвятоСлав5")

# {
#     "dishes": []
# }
# Аварийная копия пустой базы данных (мне проста лень каждый раз заново писать, я поэтому отсюда копирую)