from dataclasses import dataclass

@dataclass(frozen=True)
class Unit:
    name: str
    alternatives: dict[str: int|float]

@dataclass(frozen=True)
class Ingredient:
    name: str
    unit: [Unit]

@dataclass(frozen=True)
class Device:
    name: str

@dataclass(frozen=True)
class Preference:
    name: str

@dataclass(frozen=True)
class FoodType:
    name: str

@dataclass(frozen=True)
class Dish:
    id: int
    name: str
    food_type: FoodType
    preferences: list[Preference]
    food_device: Device
    ingredients: dict[Ingredient: int]
    cooking_time: int
    eating_time: int