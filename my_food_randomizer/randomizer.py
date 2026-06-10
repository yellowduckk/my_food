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

    # def recursive_randomize(self, count_of_dishes: int, list_food: list[Dish], forbidden_food: list[Dish], shedule: list[Dish], shedule_length: int, meat_flag: bool):
    #     if shedule_length >= count_of_dishes:
    #         return []
    #     if shedule_length < count_of_dishes:
    #         condidate = random.choice(list_food)
    #         if condidate in shedule or condidate in forbidden_food:
    #             while condidate in shedule or condidate in forbidden_food:
    #                 condidate = random.choice(list_food)
    #         length = shedule_length + condidate.eating_time
    #         if length <= count_of_dishes or (meat_flag is False):
    #             return self.recursive_randomize(count_of_dishes, list_food, forbidden_food, shedule + [condidate], length, meat_flag) + [condidate]
    #         else:
    #             return self.recursive_randomize(count_of_dishes, list_food, forbidden_food, shedule, shedule_length, meat_flag)

    def linear_randomize(self, count_of_dishes: int, used_food: list[Dish], list_food: list[Dish]):
        unused_food = list_food
        if used_food != []: unused_food = [elem for elem in list_food if elem not in used_food]
        shedule = []
        count_of_dishes_in_shedule = 0
        while count_of_dishes_in_shedule < count_of_dishes:
            condidate = random.choice(unused_food)
            if condidate.eating_time > count_of_dishes - count_of_dishes_in_shedule:
                break_count = 0
                while condidate.eating_time > count_of_dishes - count_of_dishes_in_shedule and break_count < 100:
                    condidate = random.choice(unused_food)
                    break_count += 1
            shedule.append(condidate)
            unused_food.pop(unused_food.index(condidate))
            count_of_dishes_in_shedule += condidate.eating_time
        return shedule

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

        # list_food_breakfasts = self.recursive_randomize(count_of_dishes, breakfasts, [], [], 0, False)
        # list_food_garnish = self.recursive_randomize(count_of_dishes, garnish, [], [], 0, False)
        # list_food_meat = []
        # for elem in list_food_garnish:
        #     list_food_meat += self.recursive_randomize(elem.eating_time, meat, list_food_meat, [], 0, True)
        # list_food_others = self.recursive_randomize(count_of_dishes // 2, others, [], [], 0, False) + [random.choice(fruits)]

        list_food_breakfasts = self.linear_randomize(count_of_dishes, [], breakfasts)
        list_food_garnish = self.linear_randomize(count_of_dishes, [], garnish)
        list_food_meat = []
        for elem in list_food_garnish:
            list_food_meat += self.linear_randomize(elem.eating_time, list_food_meat, meat)
        list_food_others = self.linear_randomize(count_of_dishes, [], others) + [random.choice(fruits)]

        return (list_food_breakfasts, list_food_garnish, list_food_meat, list_food_others)
# Создаёт расписание
# Подходящие блюда задаются либо способом приготовления, либо типом еды