from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass


class FoodType(str, Enum):
    MEAT = "мясо"
    FISH = "рыба"
    FRUIT = "фрукт"
    DESSERT = "сладкое"
    SALAD = "салат"

class FoodDevice(str, Enum):
    OVEN = "духовка"
    STOVE = "плита"
    AEROGRILL = "аэрогриль"

@dataclass(frozen=True)
class Dish:
    id: int
    name: str
    food_type: FoodType
    food_device: FoodDevice
    cooking_time: timedelta
    eating_time: timedelta



