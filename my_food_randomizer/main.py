from my_food_randomizer.dish_classes import FoodDevice, Preference
from my_food_randomizer.load_dishes import load_dish
from my_food_randomizer.randomizer import WeekGenerator

def main():
    dishes = load_dish()
    wg = WeekGenerator(dishes)
    list_of_food = wg.get_shedule(7, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))
    for food in list_of_food:
        print(*food, sep="\n")
        print("----")

if __name__ == '__main__':
    main()



