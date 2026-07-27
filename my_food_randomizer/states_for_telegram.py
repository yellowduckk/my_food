import telebot
from telebot.handler_backends import State, StatesGroup


class DishAdderStates(StatesGroup):
    starting = State()
    dish_naming = State()
    type_selecting = State()
    type_naming = State()
    preferences_selecting = State()
    device_selecting = State()
    device_naming = State()
    ingredients_selecting = State()
    new_ingredients_selecting = State() #
    ingredients_naming = State() #
    quantity_adding = State()
    cooking_time_adding = State()
    eating_time_adding = State()