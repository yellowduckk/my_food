import random

from my_food_randomizer.dish_classes import FoodType, FoodDevice
from my_food_randomizer.load_dishes import load_dishes
from my_food_randomizer.randomizer import WeekGenerator


def main():
    dishes = load_dishes()
    wg = WeekGenerator(dishes)
    #h = wg._get_candidates_food_type(FoodType("мясо"))
    #r = wg._get_candidates_food_device(FoodDevice("духовка"))
    list_of_food = wg.randomize()

    for food in list_of_food:
        print(food)


if __name__ == '__main__':
    main()


