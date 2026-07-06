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

    def _count_eating_time(self, list_food: list[Dish], remaining_time: int, flag_return: bool) -> list[Dish]:
        """
        :param list_food: список блюд, которые можно использовать
        :param remaining_time: время, которое нужно занять одним блюдом
        :return: если возможно, список еды, поедание которой занимает время, которое нужно занять, иначе весь список блюд, переданный изначально
        """
        all_eating_times = set()
        # print(list_food)
        for food in list_food:
            all_eating_times.add(food.eating_time)
        all_eating_times = list(all_eating_times)
        # print(all_eating_times)
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
        if flag_return:
            return []
        else:
            return list_food

    def _randomize(self, period_eating_time: (int, timedelta), used_food: list[Dish], list_food: list[Dish]) -> (List[Dish], bool):
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
            # print(list_food)
            # print(unused_food)

        shedule = []
        summary_eating_time = 0
        while summary_eating_time < period_eating_time:
            remaining_time = period_eating_time - summary_eating_time
            if list_food == []:
                # # if backup_list_food:
                # #     list_food = list(backup_list_food)
                #     if shedule:
                #         list_food.remove(shedule[-1])
                # else:
                return shedule, False
                # list_food = list(backup_list_food)
                # if shedule and len(list_food) > 1:
                #     list_food.remove(shedule[-1])
            condidates = self._count_eating_time(list_food, remaining_time, False)
            condidate = random.choice(condidates)
            shedule.append(condidate)
            list_food.remove(condidate)
            summary_eating_time += condidate.eating_time
        return shedule, True

    def _lists_of_food_to_string(self, list_food_breakfasts: list[Dish], dict_food_meat: dict[str: Dish], list_food_garnish, list_food_meat,  list_food_others: list[Dish], flag_b, flag_m, flag_o) -> str:
        list_food_breakfasts_names, list_food_garnish_strings, list_meat_names, list_food_others_names = [], [], [], []
        b_string, g_string, o_string = "", "", ""
        b_string_error, g_string_error, o_string_error = "", "", ""
        if not flag_b:
            b_string_error = "\n(В базе данных недостаточно блюд такого типа для созднаия расписания на такое время)"
        if not flag_m:
            g_string_error = "\n(В базе данных недостаточно блюд такого типа для созднаия расписания на такое время)"
        if not flag_o:
            o_string_error = "\n(В базе данных недостаточно блюд такого типа для созднаия расписания на такое время)"
        if list_food_breakfasts:
            for food in list_food_breakfasts:
                list_food_breakfasts_names.append(food.name)
            b_string = "<b>Завтраки:</b>\n- "
        else:
            list_food_breakfasts_names = ["Недостаточно девайсов для приготовления завтрака"]
            b_string = "<b>Завтраки:</b>\n"
        if list_food_garnish:
            if dict_food_meat:
                for food in list_food_meat:
                    # for meat in dict_food_meat[food.name]:
                    garnish = dict_food_meat[food.name]
                    # list_meat_names += [meat.name]
                    garnish_and_meat_string = garnish.name + " и " + food.name
                    # list_meat_names = []
                    list_food_garnish_strings.append(garnish_and_meat_string)
                g_string = "\n<b>Блюда:</b>\n- "
            else:
                for food in list_food_garnish:
                    list_food_garnish_strings.append(food.name)
                g_string = "\n<b>Гарниры (недостаточно девайсов для приготовления мяса и рыбы):</b>\n- "
        elif list_food_meat:
            for food in list_food_meat:
                list_food_garnish_strings.append(food.name)
            g_string = "\n<b>Мясо и рыба (недостаточно девайсов для приготовления гарниров):</b>\n- "
        else:
            list_food_garnish_strings = ["Недостаточно девайсов для приготовления мяса и гарниров"]
            g_string = "\n<b>Блюда:</b>\n"
        if list_food_others:
            for food in list_food_others:
                list_food_others_names.append(food.name)
            o_string = "\n<b>Другое:</b>\n- "
        else:
            list_food_others_names =["Недостаточно девайсов для приготовления дополнительных блюд"]
            o_string = "\n<b>Другое:</b>\n"
        shedule = b_string + "\n- ".join(list_food_breakfasts_names) + b_string_error + g_string + "\n- ".join(list_food_garnish_strings) + g_string_error + o_string + "\n- ".join(list_food_others_names) + o_string_error
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

        print("--")
        print(breakfasts)
        print(garnish)
        print(meat)
        print(fruits)
        print(desserts)
        print(snacks)
        print(salads)
        print("--")

        list_food_breakfasts, flag_b = self._randomize(period_eating_time, [], list(breakfasts))

        if meat:
            list_food_meat, flag_m = self._randomize(period_eating_time, [], list(meat))
            print(list_food_meat)
            for i in list_food_meat:
                print(i.name)
            if garnish:
                dict_food_meat = {}
                list_food_garnish = []
                list_food_unused_garnish = list(garnish)
                for meat_from_list in list_food_meat:
                    print(meat_from_list.name)
                    # new_garnish_from_list = self._randomize(meat_from_list.eating_time, list_food_garnish, list(garnish), list(garnish))
                    suitable_garnish = self._count_eating_time(list_food_unused_garnish, meat_from_list.eating_time, True)
                    if suitable_garnish == []:
                        list_food_unused_garnish = list(garnish)
                        suitable_garnish = self._count_eating_time(list_food_unused_garnish, meat_from_list.eating_time, True)
                    new_garnish_from_list = random.choice(suitable_garnish)
                    list_food_garnish += [new_garnish_from_list]
                    list_food_unused_garnish.remove(new_garnish_from_list)
                    dict_food_meat[meat_from_list.name] = new_garnish_from_list
            else:
                dict_food_meat = {}
                list_food_meat = []
                flag_m = True
                list_food_garnish = []
        elif garnish:
            dict_food_meat = {}
            list_food_meat = []
            flag_m = True
            list_food_garnish = self._randomize(period_eating_time, [], list(garnish))
        else:
            dict_food_meat = {}
            list_food_meat = []
            flag_m = True
            list_food_garnish = []


        # if garnish:
        #     list_food_garnish = self._randomize(period_eating_time, [], list(garnish), list(garnish))
        #     if meat:
        #         dict_food_meat = {}
        #         dict_food_meat_new = {}
        #         list_food_meat = []
        #         for garnish_from_list in list_food_garnish:
        #             new_meat_for_garnish = self._randomize(garnish_from_list.eating_time, list_food_meat, list(meat), [])
        #             # print("-", list_food_meat)
        #             list_food_meat += new_meat_for_garnish
        #             # print("-", new_meat_for_garnish)
        #             dict_food_meat[garnish_from_list.name] = new_meat_for_garnish
        #             print(list_food_meat)
        #             if list_food_meat == meat:
        #                 break
        #         unused_garnish = list(garnish)
        #         # print("-", unused_garnish, garnish)
        #         for used_garnish in list_food_garnish:
        #             if used_garnish in unused_garnish:
        #                 unused_garnish.remove(used_garnish)
        #
        #         for garnish_from_dict in dict_food_meat.keys():
        #             if len(dict_food_meat[garnish_from_dict]) > 1:
        #                 for meat_index in range(1, len(dict_food_meat[garnish_from_dict])):
        #                     if unused_garnish == []:
        #                         unused_garnish = list(garnish)
        #                     # print(unused_garnish)
        #                     # suitable_unused_garnish = self._count_eating_time(unused_garnish, dict_food_meat[garnish_from_dict][meat_index].eating_time)
        #                     # if suitable_unused_garnish == []:
        #                     #     unused_garnish = list(garnish)
        #                     suitable_unused_garnish = self._count_eating_time(unused_garnish, dict_food_meat[garnish_from_dict][meat_index].eating_time)
        #                     # print(unused_garnish)
        #                     # print(suitable_unused_garnish)
        #                     # print(random.choice(suitable_unused_garnish))
        #                     suitable_unused_garnish_choised = random.choice(suitable_unused_garnish)
        #                     dict_food_meat_new[suitable_unused_garnish_choised.name] = dict_food_meat[garnish_from_dict][meat_index]
        #                     unused_garnish.remove(suitable_unused_garnish_choised)
        #                 # print(list(dict_food_meat[garnish_from_dict]))
        #                 dict_food_meat[garnish_from_dict] = [dict_food_meat[garnish_from_dict][0]]
        #         dict_food_meat = dict_food_meat_new | dict_food_meat
        #     else:
        #         dict_food_meat = {}
        # elif meat:
        #     dict_food_meat = {}
        #     dict_food_meat["мясо"] = self._randomize(period_eating_time, [], list(meat), [])
        #     list_food_garnish = []
        # else:
        #     dict_food_meat = {}
        #     list_food_garnish = []

        # print(desserts)
        list_food_others = []
        for list_food in [fruits, salads, snacks, desserts]:
            if list_food:
                list_food_others.append(random.choice(list_food))
        flag_o = (len(list_food_others) == 4)

        shedule = self._lists_of_food_to_string(list_food_breakfasts, dict_food_meat, list_food_garnish, list_food_meat, list_food_others, flag_b, flag_m, flag_o)

        return shedule