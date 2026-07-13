from datetime import timedelta
from enum import Enum
from dataclasses import dataclass


# class FoodType(str, Enum):
#     MEAT = "мясо"
#     FISH = "рыба"
#     FRUIT = "фрукт"
#     DESSERT = "сладкое"
#     SALAD = "салат"
#     GARNISH = "гарнир"
#     BREAKFAST = "завтрак"
#     SNACK = "закуска"
#     LIQUID = "жидкое"
#     # Расшифровка всех видов еды
#
# class FoodDevice(str, Enum):
#     OVEN = "духовка"
#     STOVE = "плита"
#     AEROGRILL = "аэрогриль"
#     FRIDGE = "холодильник"
#     NUKE = "микроволновка"
#     MULTICOOKER = "мультиварка"
#     # Расшифровка всех способов приготовления
#
# class Preference(str, Enum):
#     SUMMER = "лето"
#     AUTUMN = "осень"
#     WINTER = "зима"
#     SPRING = "весна"
#     # Расшифровка всех предпочтений

# @dataclass(frozen=True)
# class Ingredient:
#     ingredient: str
#     unit_of_measurement: str
#
# @dataclass(frozen=True)
# class FoodType:
#     food_type: str
#
# @dataclass(frozen=True)
# class FoodDevice:
#     food_device: str
#
# @dataclass(frozen=True)
# class Preference:
#     preference: str
#
# @dataclass(frozen=True)
# class Dish:
#     id: int
#     name: str
#     food_type: FoodType
#     preferences: list[Preference]
#     food_device: FoodDevice
#     ingredients: dict
#     cooking_time: timedelta
#     eating_time: timedelta
# Шаблон блюда