from my_food_randomizer.dish_classes import FoodType, FoodDevice, Preference
from my_food_randomizer.load_dishes import load_dish
from my_food_randomizer.randomizer import WeekGenerator

def main():
    dishes = load_dish()
    wg = WeekGenerator(dishes)
    list_of_fruits = wg.randomize(7, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))
    for elem in list_of_fruits:
        print(*elem, sep="\n")
        print("----")

    # for i in dishes:
    #     if i.food_type in ["мясо", "рыба"]:
    #         print(i)

if __name__ == '__main__':
    main()



