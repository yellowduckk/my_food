import random
from typing import List
from datetime import timedelta
from my_food_randomizer.dish_classes import Dish, FoodDevice, Preference


class WeekGenerator:
    def __init__(self, dishes: List[Dish]):
        self.dishes = dishes # Вся еда


    def _get_candidates(self, preferences: list[Preference], food_device: list[FoodDevice]) -> list[Dish]:
        """
        :param preference: предпочтения в еде
        :param food_device: устройство, на котором готовят блюдо
        :return: список блюд, подходящих по предпочтениям и девайсу
        """
        suitable_foods = []
        for dish_food in self.dishes:
            if (dish_food.food_device in food_device or dish_food.food_device == "-") and self._check_preferences(dish_food.preferences, preferences) is True:
                suitable_foods.append(dish_food)
        return suitable_foods

    def _check_preferences(self, food_preferences: list[Preference], preferences: list[Preference]) -> bool:
        """
        :param food_preferences: предпочнения, которым соответсвтует еда
        :param preferences: предпочтения в еде
        :return: результат проверки соответсвия предпочений, которым соответсвтует еда и предпочтений в еде
        """
        for preference in food_preferences:
            if preference in preferences:
                return True
        return False

    def _count_eating_time(self, list_food: list[Dish], remaining_time: int) -> list[Dish]:
        """
        :param list_food: список блюд, которые можно использовать
        :param remaining_time: время, которое нужно занять одним блюдом
        :return: если возможно, список еды, поедание которой занимает время, которое нужно занять, иначе весь список блюд, переданный изначально
        """
        all_eating_times = list(set([elem.eating_time for elem in list_food]))
        print(all_eating_times)
        suitable_food = []
        if remaining_time in all_eating_times:
            for food in list_food:
                if food.eating_time == remaining_time:
                    suitable_food.append(food)
            return suitable_food
        else:
            if max(all_eating_times) > remaining_time:
                for food in list_food:
                    if food.eating_time > remaining_time:
                        suitable_food.append(food)
                return suitable_food
            return list_food

    def _randomize(self, period_eating_time: (int, timedelta), used_food: list[Dish], list_food: list[Dish], backup_list_food: list[Dish]) -> List[Dish]:
        """
        :param period_eating_time: время, на которое нужно составить расписание
        :param used_food: еда того же типа, которая уже была использована в расписании
        :param list_food: список еды одного типа
        :return: расписание по одному типу еды на переданное время
        """
        if list_food == []:
            return []
        if used_food:
            unused_food = []
            for food in list_food:
                if food not in used_food:
                    unused_food.append(food)
            list_food = unused_food

        shedule = []
        summary_eating_time = 0
        while summary_eating_time < period_eating_time:
            remaining_time = period_eating_time - summary_eating_time
            if list_food == []:
                list_food = list(backup_list_food)
                if shedule:
                    list_food.remove(shedule[-1])
            condidate = random.choice(self._count_eating_time(list_food, remaining_time))
            shedule.append(condidate)
            list_food.remove(condidate)
            summary_eating_time += condidate.eating_time
        return shedule

    def _lists_of_food_to_string(self, list_food_breakfasts: list[Dish], dict_food_meat: dict[str: Dish], list_food_garnish,  list_food_others: list[Dish]) -> str:
        list_food_breakfasts_names, list_food_garnish_strings, list_meat_names, list_food_others_names = [], [], [], []
        for food in list_food_breakfasts:
            list_food_breakfasts_names.append(food.name)
        for food in list_food_garnish:
            for meat in dict_food_meat[food.name]:
                list_meat_names += [meat.name, str(meat.eating_time)]
            garnish_and_meat_string = food.name + str(food.eating_time) + " и " + ", ".join(list_meat_names)
            list_meat_names = []
            list_food_garnish_strings.append(garnish_and_meat_string)

        # for food in list_food_meat:
        #     list_food_meat_names.append(food.name)
        for food in list_food_others:
            list_food_others_names.append(food.name)
        shedule = "Завтраки:\n-" + "\n-".join(list_food_breakfasts_names) + "\nБлюда:\n-" + "\n-".join(list_food_garnish_strings) + "\nДругое:\n-" + "\n-".join(list_food_others_names)
        return shedule

    def get_shedule(self, period_eating_time: int, food_devices: list[FoodDevice], preference: list[Preference]) -> str:
        """
        :param period_eating_time: время, на которое нужно составить расписание
        :param food_devices: девайсы, которые можно использовать в готовке
        :param preference: сезонные предпочтения
        :return: отдельные расписания по каждому типу еды
        """
        foods = self._get_candidates(preference, food_devices)
        breakfasts, garnish, meat, fruits, desserts, snacks, salads = [], [], [], [], [], [], []
        for food in foods:
            if food.food_type == "завтрак":
                breakfasts.append(food)
            elif food.food_type == "гарнир" or food.food_type == "жидкое":
                garnish.append(food)
            elif food.food_type == "рыба" or food.food_type == "мясо":
                meat.append(food)
            elif food.food_type == "фрукт":
                fruits.append(food)
            elif food.food_type == "сладкое":
                desserts.append(food)
            elif food.food_type == "закуска":
                snacks.append(food)
            elif food.food_type == "салат":
                salads.append(food)

        list_food_breakfasts = self._randomize(period_eating_time, [], breakfasts, list(breakfasts))
        list_food_garnish = self._randomize(period_eating_time, [], garnish, list(garnish))
        dict_food_meat = {}
        list_food_meat = []
        for garnish in list_food_garnish:
            new_meat_for_garnish = self._randomize(garnish.eating_time, list_food_garnish, meat, list(meat))
            list_food_meat += new_meat_for_garnish
            dict_food_meat[garnish.name] = new_meat_for_garnish
        # list_food_others = [random.choice(fruits), random.choice(salads), random.choice(snacks), random.choice(desserts)]

        list_food_others = [random.choice(fruits), random.choice(salads), random.choice(snacks), random.choice(desserts)]

        shedule = self._lists_of_food_to_string(list_food_breakfasts, dict_food_meat, list_food_garnish, list_food_others)

        return shedule