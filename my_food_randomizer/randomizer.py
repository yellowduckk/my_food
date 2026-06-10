import random
from typing import List
from my_food_randomizer.dish_classes import Dish, FoodType, FoodDevice, Preference


class WeekGenerator:
    def __init__(self, dishes: List[Dish]):
        self.dishes = dishes # Вся еда

    def _get_candidates(self, preference: Preference, food_device: list[FoodDevice]):
        suitable_foods1 = []
        suitable_foods2 = []
        for dish_food in self.dishes:
            if dish_food.food_device in food_device or dish_food.food_device == "-":
                suitable_foods1.append(dish_food)
        for dish_food in suitable_foods1:
            if preference in dish_food.preferences:
                suitable_foods2.append(dish_food)
        return suitable_foods2

    def recursive_randomize(self, count_of_dishes: int, list_food: list[Dish], forbidden_food: list[Dish], shedule: list[Dish]):
        if len(shedule) >= count_of_dishes:
            return []
        if len(shedule) < count_of_dishes:
            condidate = random.choice(list_food)
            if (shedule != [] and condidate in shedule) or (forbidden_food != [] and condidate in forbidden_food):
                while condidate in shedule:
                    condidate = random.choice(list_food)
            mas = []
            for num in range(condidate.eating_time):
                mas.append(condidate)
            length = len(mas) + len(shedule)
            if length <= count_of_dishes or forbidden_food == []:
                return self.recursive_randomize(count_of_dishes, list_food, forbidden_food, shedule + mas) + [condidate]
            else:
                return self.recursive_randomize(count_of_dishes, list_food, forbidden_food, shedule)

    def randomize(self, count_of_dishes: int, food_devices: list[FoodDevice], preference: Preference):
        foods = self._get_candidates(preference, food_devices)

        breakfasts = []
        garnish = []
        meat = []
        fruits = []
        others = []
        for food in foods:
            if food.food_type == "завтрак":
                breakfasts.append(food)
            elif food.food_type == "гарнир" or food.food_type == "жидкое":
                garnish.append(food)
            elif food.food_type == "рыба" or food.food_type == "мясо":
                meat.append(food)
            elif food.food_type == "фрукт":
                fruits.append(food)
            else:
                others.append(food)

        list_food_breakfasts = self.recursive_randomize(count_of_dishes, breakfasts, [], [])
        list_food_garnish = self.recursive_randomize(count_of_dishes, garnish, [], [])
        list_food_meat = []
        for elem in list_food_garnish:
            list_food_meat += self.recursive_randomize(elem.eating_time, meat, list_food_meat, [])
        list_food_others = self.recursive_randomize(count_of_dishes // 2, others, [], []) + [random.choice(fruits)]

        return (list_food_breakfasts, list_food_garnish, list_food_meat, list_food_others)
# Создаёт расписание
# Подходящие блюда задаются либо способом приготовления, либо типом еды