import random

from my_food_randomizer.dish_classes import FoodType, FoodDevice, Preference
from my_food_randomizer.load_dishes import load_dish
from my_food_randomizer.randomizer import WeekGenerator

def find_type_of_food(list_of_food: list, food_type: str = "фрукт"):
    flag = False
    for food in list_of_food:
        if food_type in food.food_type:
            flag = True
            break
        else:
            pass
    return flag


def main():
    dishes = load_dish()
    wg = WeekGenerator(dishes)
    #r = wg._get_candidates_food_device(FoodDevice("духовка"))
    #list_of_meat = wg.randomize(5, "food_type", FoodType("мясо"))
    #list_of_fruits = wg.randomize(5, "food_type", FoodType("фрукт"))

    list_of_food = wg.randomize(6, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))

    is_fruit = find_type_of_food(list_of_food)
    if not is_fruit:
        fruits = wg.randomize(2, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))
        for fruit in fruits:
            list_of_food.append(fruit)
    #TODO подумать как совместить гарнир с мясом
    #TODO добавить тэги по сезонным хотелкам
    """
    is_garnish = find_type_of_food(list_of_food, "гарнир")
    if is_garnish:
        meats = wg.randomize(3, "food_type", FoodType("мясо"))
        for meat in meats:
            list_of_food.append(meat)
    """

    # for food in list_of_food:
    #     print(food)

# print(*load_dish(), sep="\n")
for i in load_dish():
     if i.food_type == "сладкое":
        print(i)


if __name__ == '__main__':
    main()



