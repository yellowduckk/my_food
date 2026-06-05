import random
from typing import List
from my_food_randomizer.dish_classes import Dish, FoodType, FoodDevice, Preference


class WeekGenerator:
    def __init__(self, dishes: List[Dish]):
        self.dishes = dishes # Вся еда

    def _get_candidates_food_type(self, food_type: FoodType):
        suitable_foods = []
        for dish in self.dishes:
            if dish.food_type == food_type:
                suitable_foods.append(dish)
        return suitable_foods
# Подбирает еду по типу

    def _get_candidates_food_device(self, food_devices: list[FoodDevice]):
        suitable_foods = []
        for dish in self.dishes:
            if dish.food_device in food_devices:
                suitable_foods.append(dish)
        return suitable_foods
# Подбирает еду по способу приготовления

    def _get_candidates_preferences(self, preference: Preference):
        suitable_foods = []
        for dish_food in self.dishes:
            if preference in dish_food.preferences:
                suitable_foods.append(dish_food)
        return suitable_foods



    def randomize(self, count_of_dishes: int, food_devices: list[FoodDevice], preference: Preference):
        foods = self._get_candidates_food_device(food_devices)
        foods = self._get_candidates_preferences(preference)

        list_food = []
        for i in range(count_of_dishes):
            temp_dish = random.choice(foods)
            if temp_dish not in list_food:
                list_food.append(temp_dish)

        return list_food
# Создаёт расписание
# Подходящие блюда задаются либо способом приготовления, либо типом еды