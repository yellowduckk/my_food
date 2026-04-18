import random
from typing import List
from my_food_randomizer.dish_classes import Dish, FoodType, FoodDevice


class WeekGenerator:
    def __init__(self, dishes: List[Dish]):
        self.dishes = dishes

    def _get_candidates_food_type(self, food_type: FoodType):
        suitable_foods = []
        for dish in self.dishes:
            if dish.food_type == food_type:
                suitable_foods.append(dish)
        return suitable_foods

    def _get_candidates_food_device(self, food_device: FoodDevice):
        suitable_foods = []
        for dish in self.dishes:
            if dish.food_device == food_device:
                suitable_foods.append(dish)
        return suitable_foods

    def randomize(self, count_of_dishes=6, flag="", food_type=None, food_device=None):
        if flag == "food_type":
            foods = self._get_candidates_food_type(food_type)
        elif flag == "food_device":
            foods = self._get_candidates_food_device(food_device)
        else:
            foods = self.dishes

        list_food = []
        for i in range(count_of_dishes):
            temp_dish = random.choice(foods)
            if temp_dish not in list_food:
                list_food.append(temp_dish)

        return list_food