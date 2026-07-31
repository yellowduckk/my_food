from my_food_json_files import Dish, FoodType, Preference, Device, Ingredient, AddDish, DishLoader
from states_for_telegram import DishAdderStates

import telebot
from telebot import types, custom_filters
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import datetime

from randomizer import WeekGenerator

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token="8957694347:AAFIMl1W8lkPp1JcVgd9b_rBnipFk7-x_xo", state_storage=state_storage)

def main():
    users_devices = {}
    users_dishes = {}
    dishes = DishLoader().load_dish()
    dishes_names = [dish.name for dish in dishes]
    dish_loader = DishLoader()
    dish_adder = AddDish(dish_loader.load_dish(), dish_loader.load_ingredients(), dish_loader.load_preferences(), dish_loader.load_food_types(), dish_loader.load_food_devices())
    week_gen = WeekGenerator(dishes)

    food_types = DishLoader().load_food_types()
    food_types_names = [food_type.name for food_type in food_types]
    preferences = DishLoader().load_preferences()
    preferences_names = [preference.name for preference in preferences]
    ingredients = DishLoader().load_ingredients()
    ingredients_names = [ingredient.name for ingredient in ingredients]
    users_current_indexes = {}
    users_poll_options = {}

    months_numbers_to_seasons = {1: "зима", 2: "зима", 3: "весна", 4: "весна", 5: "весна", 6: "лето", 7: "лето", 8: "лето", 9: "осень", 10: "осень", 11: "осень", 12: "зима"}
    polls_messages_ids = {}
    polls_messages_ids_for_dish_adding = {}
    all_food_devices = []
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_callback = CallbackData("calendar", "action", "year", "month", "day")
    # keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_shedule = telebot.types.InlineKeyboardButton(text="Создать расписание", callback_data="shedule")
    button_red_devices = telebot.types.InlineKeyboardButton(text="Изменить список девайсов",
                                                            callback_data="red_devices")
    button_add_dish = telebot.types.InlineKeyboardButton(text="Добавить новое блюдо", callback_data="add_dish")
    devices = DishLoader().load_food_devices()
    for device in devices:
        all_food_devices.append(device.name)
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = message.chat.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices, button_add_dish)
        if chat_id not in users_devices.keys():
            users_devices[chat_id] = all_food_devices
        devices = "\n-".join(users_devices[chat_id])
        bot.set_state(message.from_user.id, DishAdderStates.starting, chat_id)
        bot.reply_to(message, f"Привет!\n"
                          f"    Блюда в меню могут быть приготовлены с помощью этих девайсов:\n-{devices}\n"
                          f"Все ли эти девайсы есть у вас в наличии?\n", parse_mode="HTML", reply_markup=keyboard)
        print(message.from_user.id, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data == "shedule", state=DishAdderStates.starting)
    def shedule(call):
        chat_id = call.message.chat.id
        if chat_id not in users_devices.keys():
            users_devices[chat_id] = all_food_devices
        devices = "\n-".join(users_devices[chat_id])
        bot.send_message(chat_id, f"    Меню будет составлено с учётом наличия этих девайсов:\n-{devices}")
        today_date = datetime.datetime.now()
        bot.send_message(chat_id,"Выберите дату окончания расписания", reply_markup=calendar.create_calendar(name=calendar_callback.prefix, year=today_date.year, month=today_date.month))

    @bot.callback_query_handler(func=lambda call: call.data == "red_devices", state=DishAdderStates.starting)
    def red_devices(call):
        chat_id = call.message.chat.id
        devices_names_length = len(all_food_devices)
        if devices_names_length > 11:
            number = devices_names_length - 11
            users_current_indexes[chat_id] = (number, 1)
            poll_message = bot.send_poll(chat_id=chat_id, question="Выберете девайсы, которые есть у вас в наличии",
                                         options=all_food_devices[:11] + ["пропуск"], is_anonymous=False, allows_multiple_answers=True)
            polls_messages_ids[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = all_food_devices[:11] + ["пропуск"]
        else:
            users_current_indexes[chat_id] = (0, 0)
            poll_message = bot.send_poll(chat_id=chat_id, question="Выберете девайсы, которые есть у вас в наличии",
                                         options=all_food_devices + ["пропуск"], is_anonymous=False, allows_multiple_answers=True)
            polls_messages_ids[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = all_food_devices + ["пропуск"]
        users_devices[chat_id] = []
        polls_messages_ids[chat_id] = poll_message.message_id

    @bot.callback_query_handler(func=lambda call: call.data == "add_dish", state=DishAdderStates.starting)
    def begin_dish_adding(call):
        chat_id = call.message.chat.id
        bot.set_state(call.from_user.id, DishAdderStates.dish_naming, chat_id)
        bot.send_message(chat_id, f"Введите название нового блюда\n"
                                  f"Оно не должно совпадать с названиями имеющихся блюд:\n-{"\n-".join(dishes_names)}", parse_mode="HTML")
        print(bot.get_state(call.from_user.id, chat_id))

    @bot.poll_answer_handler(state=DishAdderStates.starting)
    def handle_poll(poll):
        chat_id = poll.user.id
        selected_options_ids = poll.option_ids
        selected_devices = []
        for option_id in selected_options_ids:
            if users_poll_options[chat_id][option_id] != "пропуск":
                selected_devices.append(users_poll_options[chat_id][option_id])
        print(selected_devices)
        users_devices[chat_id] += selected_devices
        devices_names_length = users_current_indexes[chat_id][0]
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids[chat_id])
        if devices_names_length > 11:
            number = devices_names_length - 11
            count_11 = users_current_indexes[chat_id][1]
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете девайсы, которые есть у вас в наличии",
                                         options=all_food_devices[11 * count_11: 11 * (count_11 + 1)] + ["пропуск"],
                                         is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
            users_current_indexes[chat_id] = (number, count_11 + 1)
            users_poll_options[chat_id] = all_food_devices[11 * count_11: 11 * (count_11 + 1)] + ["пропуск"]
        elif devices_names_length > 0:
            count_11 = users_current_indexes[chat_id][1]
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете девайсы, которые есть у вас в наличии",
                                         options=all_food_devices[11 * count_11: len(all_food_devices)] + ["пропуск"],
                                         is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = all_food_devices[11 * count_11: len(all_food_devices)] + ["пропуск"]
            users_current_indexes[chat_id] = (0, 0)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(button_shedule, button_red_devices, button_add_dish)
            devices = "\n-".join(users_devices[chat_id])
            bot.send_message(chat_id, f"Выбраны девайсы:\n-{devices}", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix), state=DishAdderStates.starting)
    def callback_inline(call: types.CallbackQuery):
        chat_id = call.from_user.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices, button_add_dish)
        today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        name, action, year, month, day = call.data.split(calendar_callback.sep)
        date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == "DAY":
            days_to_date = (date - today_date).days + 1
            if date >= today_date and days_to_date <= 30:
                bot.send_message(chat_id, f"Выбрана дата {date.strftime('%d.%m.%Y')}, расписание будет составлено на {days_to_date} дней", reply_markup=types.ReplyKeyboardRemove())
                months_to_date = (date.year - today_date.year) * 12 + date.month - today_date.month + 1
                seasons = set()
                for month in range(today_date.month, today_date.month + months_to_date + 1):
                    seasons.add(months_numbers_to_seasons[month])
                seasons = list(seasons)
                print(seasons)
                preferences = []
                if seasons:
                    for season in seasons:
                        preferences.append(Preference(season))
                else:
                    preferences = [Preference(months_numbers_to_seasons[date.month])]
                food_devices = []
                for device in users_devices[chat_id]:
                    food_devices.append(Device(device))
                list_of_food = week_gen.get_shedule(days_to_date, food_devices, preferences)
                print(list_of_food)
                print(days_to_date)
                bot.send_message(chat_id, list_of_food, parse_mode="HTML", reply_markup=keyboard)
            else:
                print(date, today_date)
                bot.send_message(chat_id, "Нельзя выбрать эту дату", reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(chat_id, "Хотите создать новое расписание или отредактировать список использованых девайсов?", reply_markup=keyboard)
        elif action == "CANCEL":
            bot.send_message(chat_id, "Выбор даты отменён", reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id,
                             "Хотите создать новое расписание или отредактировать список использованых девайсов?",
                             reply_markup=keyboard)

    @bot.message_handler(state=DishAdderStates.dish_naming)
    def name_handler(message):
        chat_id = message.chat.id
        new_name = message.text.lower()
        users_dishes[chat_id] = []
        print(new_name)
        if new_name in dishes_names:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(button_shedule, button_red_devices, button_add_dish)
            bot.set_state(message.from_user.id, DishAdderStates.starting, chat_id)
            bot.send_message(chat_id, "Блюдо с таким названием уже существует", reply_markup=keyboard)
        else:
            users_dishes[chat_id].append(new_name)
            food_types_names_length = len(all_food_devices)
            if food_types_names_length > 11:
                number = food_types_names_length - 11
                users_current_indexes[chat_id] = (number, 1)
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите тип блюда",
                                             options=food_types_names[:11] + ["другое"], is_anonymous=False,
                                             allows_multiple_answers=False)
                users_poll_options[chat_id] = ingredients_names[:11] + ["пропуск"]
            else:
                users_current_indexes[chat_id] = (0, 0)
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите тип блюда",
                                             options=food_types_names + ["другое"], is_anonymous=False,
                                             allows_multiple_answers=False)
                users_poll_options[chat_id] = food_types_names + ["другое"]
            bot.set_state(message.from_user.id, DishAdderStates.type_selecting, chat_id)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id

    @bot.poll_answer_handler(state=DishAdderStates.type_selecting)
    def handle_type_selecting(poll):
        chat_id = poll.user.id
        selected_option_id = poll.option_ids[0]
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids_for_dish_adding[chat_id])
        if selected_option_id != len(users_poll_options[chat_id]) - 1:
            selected_type = users_poll_options[chat_id][selected_option_id]
            users_dishes[chat_id].append(selected_type)
            bot.set_state(chat_id, DishAdderStates.preferences_selecting, chat_id)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете времена года, в которые можно есть ваше блюдо",
                                         options=preferences_names, is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
        else:
            types_names_length = users_current_indexes[chat_id][0]
            if types_names_length == 0:
                bot.set_state(chat_id, DishAdderStates.type_naming, chat_id)
                bot.send_message(chat_id, "Введите тип блюда")
            elif types_names_length < 11:
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите тип блюда",
                                             options=food_types_names[11 * count_11: len(all_food_devices)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_poll_options[chat_id] = all_food_devices[11 * count_11: len(all_food_devices)] + ["другое"]
                users_current_indexes[chat_id] = (0, 0)
            else:
                number = types_names_length - 11
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите тип блюда",
                                             options=food_types_names[11 * count_11: 11 * (count_11 + 1)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_current_indexes[chat_id] = (number, count_11 + 1)
                users_poll_options[chat_id] = food_types_names[11 * count_11: 11 * (count_11 + 1)] + ["другое"]

    @bot.message_handler(state=DishAdderStates.type_naming)
    def type_naming_handler(message):
        chat_id = message.chat.id
        users_dishes[chat_id].append(message.text.lower())
        print(message.text)
        bot.set_state(message.from_user.id, DishAdderStates.preferences_selecting, chat_id)
        poll_message = bot.send_poll(chat_id=chat_id, question="Выберете времена года, в которые можно есть ваше блюдо",
                                     options=preferences_names, is_anonymous=False,
                                     allows_multiple_answers=True)
        polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id

    @bot.poll_answer_handler(state=DishAdderStates.preferences_selecting)
    def preferences_selecting(poll):
        chat_id = poll.user.id
        selected_options_ids = poll.option_ids
        selected_preferences = []
        for selected_option_id in selected_options_ids:
            selected_preferences.append(preferences_names[selected_option_id])
        users_dishes[chat_id].append(selected_preferences)
        bot.set_state(chat_id, DishAdderStates.device_selecting, chat_id)
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids_for_dish_adding[chat_id])
        devices_names_length = len(all_food_devices)
        if devices_names_length > 11:
            number = devices_names_length - 11
            users_current_indexes[chat_id] = (number, 1)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберите девайс, необходимый для приготовления блюда",
                                         options=all_food_devices[:11] + ["другое"], is_anonymous=False,
                                         allows_multiple_answers=False)
            users_poll_options[chat_id] = ingredients_names[:11] + ["пропуск"]
        else:
            users_current_indexes[chat_id] = (0, 0)
            poll_message = bot.send_poll(chat_id=chat_id, question="Выберите девайс, необходимый для приготовления блюда",
                                         options=all_food_devices + ["другое"], is_anonymous=False,
                                         allows_multiple_answers=False)
            users_poll_options[chat_id] = all_food_devices + ["другое"]
        polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id

    @bot.poll_answer_handler(state=DishAdderStates.device_selecting)
    def device_selecting_handler(poll):
        chat_id = poll.user.id
        selected_option_id = poll.option_ids[0]
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids_for_dish_adding[chat_id])
        if selected_option_id != len(users_poll_options[chat_id]) - 1:
            selected_device = users_poll_options[chat_id][selected_option_id]
            users_dishes[chat_id].append(selected_device)
            bot.set_state(chat_id, DishAdderStates.ingredients_selecting, chat_id)
            ingredients_names_length = len(ingredients_names)
            if ingredients_names_length > 11:
                number = ingredients_names_length - 11
                users_current_indexes[chat_id] = (number, 1)
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                             options=ingredients_names[:11] + ["пропуск"], is_anonymous=False,
                                             allows_multiple_answers=True)
                users_poll_options[chat_id] = ingredients_names[:11] + ["пропуск"]

            else:
                users_current_indexes[chat_id] = (0, 0)
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                             options=ingredients_names, is_anonymous=False,
                                             allows_multiple_answers=True)
                users_poll_options[chat_id] = ingredients_names
            users_dishes[chat_id].append([])
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
        else:
            devices_names_length = users_current_indexes[chat_id][0]
            if devices_names_length == 0:
                bot.set_state(chat_id, DishAdderStates.device_naming, chat_id)
                bot.send_message(chat_id, "Введите девайс")
            elif devices_names_length < 11:
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите девайс, необходимый для приготовления блюда",
                                             options=all_food_devices[11 * count_11: len(all_food_devices)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_poll_options[chat_id] = all_food_devices[11 * count_11: len(all_food_devices)] + ["другое"]
                users_current_indexes[chat_id] = (0, 0)
            else:
                number = devices_names_length - 11
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите девайс, необходимый для приготовления блюда",
                                             options=all_food_devices[11 * count_11: 11 * (count_11 + 1)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_current_indexes[chat_id] = (number, count_11 + 1)
                users_poll_options[chat_id] = all_food_devices[11 * count_11: 11 * (count_11 + 1)] + ["другое"]

    @bot.message_handler(state=DishAdderStates.device_naming)
    def device_naming_handler(message):
        chat_id = message.chat.id
        users_dishes[chat_id].append(message.text.lower())
        print(message.text)
        bot.set_state(message.from_user.id, DishAdderStates.ingredients_selecting, chat_id)
        ingredients_names_length = len(ingredients_names)
        if ingredients_names_length > 11:
            number = ingredients_names_length - 11
            users_current_indexes[chat_id] = (number, 1)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                         options=ingredients_names[:11] + ["пропуск"], is_anonymous=False,
                                         allows_multiple_answers=True)
            users_poll_options[chat_id] = ingredients_names[:11] + ["пропуск"]
        else:
            users_current_indexes[chat_id] = (0, 0)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                         options=ingredients_names + ["пропуск"], is_anonymous=False,
                                         allows_multiple_answers=True)
            users_poll_options[chat_id] = ingredients_names
        users_dishes[chat_id].append([])
        polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id

    @bot.poll_answer_handler(state=DishAdderStates.ingredients_selecting)
    def ingredients_selecting(poll):
        chat_id = poll.user.id
        selected_options_ids = poll.option_ids
        selected_ingredients = []
        for selected_option_id in selected_options_ids:
            if users_poll_options[chat_id][selected_option_id] != "пропуск":
                selected_ingredients.append(users_poll_options[chat_id][selected_option_id])
        users_dishes[chat_id][-1] += selected_ingredients
        ingredients_names_length = users_current_indexes[chat_id][0]
        if ingredients_names_length > 11:
            number = ingredients_names_length - 11
            count_11 = users_current_indexes[chat_id][1]
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                         options=ingredients_names[11 * count_11: 11 * (count_11 + 1)] + ["пропуск"], is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
            users_current_indexes[chat_id] = (number, count_11 + 1)
            users_poll_options[chat_id] = ingredients_names[11 * count_11: 11 * (count_11 + 1)] + ["пропуск"]
        elif ingredients_names_length > 0:
            count_11 = users_current_indexes[chat_id][1]
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете ингредиенты, из которых готовится ваше блюдо",
                                         options=ingredients_names[11 * count_11: len(ingredients_names)] + ["пропуск"], is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = ingredients_names[11 * count_11: len(ingredients_names)] + ["пропуск"]
            users_current_indexes[chat_id] = (0, 0)
        else:
            bot.set_state(chat_id, DishAdderStates.quantity_adding, chat_id)
            bot.send_message(chat_id, f"Введите количества, в которых эти ингредиенты нужны для приготовления вашего блюда (по одному числу на строку)\n"
                             f"Список ингредиентов\n-{"\n-".join(users_dishes[chat_id][-1])}")

    @bot.message_handler(state=DishAdderStates.quantity_adding)
    def quntity_adding(message):
        chat_id = message.chat.id
        dict_ingredients = {}
        quantities = message.text.split("\n")
        if len(quantities) == len(users_dishes[chat_id][-1]):
            try:
                quantities = list(map(int, quantities))
                for ingredient_ind in range(0, len(users_dishes[chat_id][-1])):
                    dict_ingredients[users_dishes[chat_id][-1][ingredient_ind]] = quantities[ingredient_ind]
                users_dishes[chat_id].pop(-1)
                users_dishes[chat_id].append(dict_ingredients)
                bot.set_state(chat_id, DishAdderStates.cooking_time_adding, chat_id)
                bot.send_message(chat_id, "Введите время, которое занимает приготовление вашего блюда")
            except ValueError:
                bot.send_message(chat_id, "Попробуйте ещё раз")
        else:
            bot.send_message(chat_id, "Попробуйте ещё раз")

    @bot.message_handler(state=DishAdderStates.cooking_time_adding)
    def cooking_time_adding(message):
        chat_id = message.chat.id
        try:
            users_dishes[chat_id].append(int(message.text))
            bot.set_state(chat_id, DishAdderStates.eating_time_adding, chat_id)
            bot.send_message(chat_id, "Введите время, за которое можно съесть ваше блюдо")
        except ValueError:
            bot.send_message(chat_id, "Попробуйте ещё раз")

    @bot.message_handler(state=DishAdderStates.eating_time_adding)
    def eating_time_adding(message):
        chat_id = message.chat.id
        try:
            users_dishes[chat_id].append(int(message.text))
            print(*users_dishes[chat_id])
            bot.set_state(chat_id, DishAdderStates.starting, chat_id)
            dish_adder.add_d(*users_dishes[chat_id])
        except ValueError:
            bot.send_message(chat_id, "Попробуйте ещё раз")



    bot.infinity_polling()

if __name__ == '__main__':
    main()