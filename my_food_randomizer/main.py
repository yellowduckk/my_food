from statistics import quantiles

from my_food_json_files import Dish, FoodType, Preference, Device, Ingredient, AddDish, DishLoader
from states_for_telegram import DishAdderStates

import telebot
from telebot import types, custom_filters
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import datetime
import re

from randomizer import WeekGenerator

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token="8957694347:AAFIMl1W8lkPp1JcVgd9b_rBnipFk7-x_xo", state_storage=state_storage)

def main():
    users_devices = {}
    users_dishes = {}
    dishes = DishLoader().load_dish()
    dishes_names = [dish.name for dish in dishes]
    dish_loader = DishLoader()
    dish_adder = AddDish(dish_loader.load_dish(), dish_loader.load_ingredients(), dish_loader.load_preferences(),
                         dish_loader.load_food_types(), dish_loader.load_food_devices(), dish_loader.load_units())
    week_gen = WeekGenerator(dishes)

    food_types = DishLoader().load_food_types()
    food_types_names = [food_type.name for food_type in food_types]
    preferences = DishLoader().load_preferences()
    preferences_names = [preference.name for preference in preferences]
    ingredients = DishLoader().load_ingredients()
    ingredients_dict = {}
    for ingredient in ingredients:
        ingredients_dict[ingredient.name] = []
        for unit in ingredient.unit:
            ingredients_dict[ingredient.name] += unit.alternatives
    units = DishLoader().load_units()
    all_units = []
    for unit in units:
        all_units += unit.alternatives
    users_current_indexes = {}
    users_poll_options = {}

    months_numbers_to_seasons = {1: "зима", 2: "зима", 3: "весна", 4: "весна", 5: "весна", 6: "лето", 7: "лето", 8: "лето", 9: "осень", 10: "осень", 11: "осень", 12: "зима"}
    polls_messages_ids = {}
    polls_messages_ids_for_dish_adding = {}
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_callback = CallbackData("calendar", "action", "year", "month", "day")
    # keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_shedule = telebot.types.InlineKeyboardButton(text="Создать расписание", callback_data="shedule")
    button_red_devices = telebot.types.InlineKeyboardButton(text="Изменить список девайсов",
                                                            callback_data="red_devices")
    button_add_dish = telebot.types.InlineKeyboardButton(text="Добавить новое блюдо", callback_data="add_dish")
    button_delete_dish = telebot.types.InlineKeyboardButton(text="Удалить блюдо", callback_data="delete_dish")
    button_yes = telebot.types.InlineKeyboardButton(text="Да", callback_data="yes")
    button_no = telebot.types.InlineKeyboardButton(text="Нет", callback_data="no")
    all_food_devices = []
    devices = DishLoader().load_food_devices()
    for device in devices:
        all_food_devices.append(device.name)
    bot.add_custom_filter(custom_filters.StateFilter(bot))

    def load_all_things():
        # global dishes, dishes_names, dish_loader, dish_adder, week_gen, food_types, food_types_names, ingredients, ingredients_dict, all_food_devices, devices
        dishes = DishLoader().load_dish()
        dishes_names = [dish.name for dish in dishes]
        dish_loader = DishLoader()
        dish_adder = AddDish(dish_loader.load_dish(), dish_loader.load_ingredients(), dish_loader.load_preferences(),
                             dish_loader.load_food_types(), dish_loader.load_food_devices(), dish_loader.load_units())
        week_gen = WeekGenerator(dishes)

        food_types = DishLoader().load_food_types()
        food_types_names = [food_type.name for food_type in food_types]
        all_food_devices = []
        devices = DishLoader().load_food_devices()
        for device in devices:
            all_food_devices.append(device.name)
        ingredients = DishLoader().load_ingredients()
        ingredients_dict = {}
        for ingredient in ingredients:
            ingredients_dict[ingredient.name] = []
            for unit in ingredient.unit:
                ingredients_dict[ingredient.name] += unit.alternatives

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = message.chat.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if dishes_names == []: keyboard.add(button_shedule, button_red_devices, button_add_dish)
        else: keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
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
        # all_food_devices = []
        # devices = DishLoader().load_food_devices()
        # for device in devices:
        #     all_food_devices.append(device.name)
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
                                         options=all_food_devices, is_anonymous=False, allows_multiple_answers=True)
            polls_messages_ids[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = all_food_devices
        users_devices[chat_id] = []
        polls_messages_ids[chat_id] = poll_message.message_id

    @bot.callback_query_handler(func=lambda call: call.data == "add_dish", state=DishAdderStates.starting)
    def begin_dish_adding(call):
        chat_id = call.message.chat.id
        bot.set_state(call.from_user.id, DishAdderStates.dish_naming, chat_id)
        dish_string = ""
        if dishes_names != []: dish_string = f"\nОно не должно совпадать с названиями имеющихся блюд:\n-{"\n-".join(dishes_names)}"
        bot.send_message(chat_id, f"Введите название нового блюда" + dish_string, parse_mode="HTML")
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
            polls_messages_ids[chat_id] = poll_message.message_id
            users_current_indexes[chat_id] = (number, count_11 + 1)
            users_poll_options[chat_id] = all_food_devices[11 * count_11: 11 * (count_11 + 1)] + ["пропуск"]
        elif devices_names_length > 0:
            count_11 = users_current_indexes[chat_id][1]
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберете девайсы, которые есть у вас в наличии",
                                         options=all_food_devices[11 * count_11: len(all_food_devices)],
                                         is_anonymous=False,
                                         allows_multiple_answers=True)
            polls_messages_ids[chat_id] = poll_message.message_id
            users_poll_options[chat_id] = all_food_devices[11 * count_11: len(all_food_devices)]
            users_current_indexes[chat_id] = (0, 0)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            if dishes_names == []: keyboard.add(button_shedule, button_red_devices, button_add_dish)
            else: keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
            if users_devices[chat_id] != []:
                devices = "\n-".join(users_devices[chat_id])
                bot.send_message(chat_id, f"Выбраны девайсы:\n-{devices}", reply_markup=keyboard)
            else:
                bot.send_message(chat_id, "Вы не выбрали ни одного девайса", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix), state=DishAdderStates.starting)
    def callback_inline(call: types.CallbackQuery):
        chat_id = call.from_user.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if dishes_names == []: keyboard.add(button_shedule, button_red_devices, button_add_dish)
        else: keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
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

    @bot.callback_query_handler(func=lambda call: call.data == "delete_dish", state=DishAdderStates.starting)
    def callback_inline(call):
        chat_id = call.from_user.id
        dishes_names_length = len(dishes_names)
        if dishes_names_length > 11:
            number = dishes_names_length - 11
            users_current_indexes[chat_id] = (number, 1)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберите блюдо, которое хотите удалить",
                                         options=dishes_names[:11] + ["другое"], is_anonymous=False,
                                         allows_multiple_answers=False)
            users_poll_options[chat_id] = dishes_names[:11] + ["другое"]
        else:
            users_current_indexes[chat_id] = (0, 0)
            poll_message = bot.send_poll(chat_id=chat_id,
                                         question="Выберите блюдо, которое хотите удалить",
                                         options=dishes_names + ["другое"], is_anonymous=False,
                                         allows_multiple_answers=False)
            users_poll_options[chat_id] = dishes_names + ["другое"]
        bot.set_state(chat_id, DishAdderStates.dish_deleting, chat_id)
        polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id

    @bot.poll_answer_handler(state=DishAdderStates.dish_deleting)
    def dish_deleting_handler(poll):
        chat_id = poll.user.id
        selected_option_id = poll.option_ids[0]
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids_for_dish_adding[chat_id])
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        if selected_option_id != len(users_poll_options[chat_id]) - 1:
            selected_dish = users_poll_options[chat_id][selected_option_id]
            dish_adder.del_d(selected_dish)
            load_all_things()
            if dishes_names == []: keyboard.add(button_shedule, button_red_devices, button_add_dish)
            else: keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
            bot.send_message(chat_id, f"Блюдо {selected_dish.name} удалено", reply_markup=keyboard)
            bot.set_state(chat_id, DishAdderStates.starting, chat_id)
        else:
            dishes_names_length = users_current_indexes[chat_id][0]
            if dishes_names_length == 0:
                bot.set_state(chat_id, DishAdderStates.starting, chat_id)
                if dishes_names == []:
                    keyboard.add(button_shedule, button_red_devices, button_add_dish)
                else:
                    keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
                bot.send_message(chat_id, "Вы не выбрали ни одного блюда")
                bot.set_state(chat_id, DishAdderStates.starting, chat_id)
            elif dishes_names_length < 11:
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите блюдо, которое хотите удалить",
                                             options=dishes_names[11 * count_11: len(dishes_names)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_poll_options[chat_id] = dishes_names[11 * count_11: len(dishes_names)] + ["другое"]
                users_current_indexes[chat_id] = (0, 0)
            else:
                number = dishes_names_length - 11
                count_11 = users_current_indexes[chat_id][1]
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите блюдо, которое хотите удалить",
                                             options=dishes_names[11 * count_11: 11 * (count_11 + 1)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_current_indexes[chat_id] = (number, count_11 + 1)
                users_poll_options[chat_id] = dishes_names[11 * count_11: 11 * (count_11 + 1)] + ["другое"]

    @bot.message_handler(state=DishAdderStates.dish_naming)
    def name_handler(message):
        chat_id = message.chat.id
        new_name = re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", message.text.lower()))
        users_dishes[chat_id] = []
        print(new_name)
        if new_name in dishes_names:
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
            if dishes_names == []:
                keyboard.add(button_shedule, button_red_devices, button_add_dish)
            else:
                keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
            bot.set_state(message.from_user.id, DishAdderStates.starting, chat_id)
            bot.send_message(chat_id, "Блюдо с таким названием уже существует", reply_markup=keyboard)
        else:
            users_dishes[chat_id].append(new_name)
            food_types_names_length = len(food_types_names)
            if food_types_names_length > 11:
                number = food_types_names_length - 11
                users_current_indexes[chat_id] = (number, 1)
                poll_message = bot.send_poll(chat_id=chat_id,
                                             question="Выберите тип блюда",
                                             options=food_types_names[:11] + ["другое"], is_anonymous=False,
                                             allows_multiple_answers=False)
                users_poll_options[chat_id] = food_types_names[:11] + ["другое"]
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
                                             options=food_types_names[11 * count_11: len(food_types_names)] + ["другое"],
                                             is_anonymous=False,
                                             allows_multiple_answers=False)
                polls_messages_ids_for_dish_adding[chat_id] = poll_message.message_id
                users_poll_options[chat_id] = food_types_names[11 * count_11: len(food_types_names)] + ["другое"]
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
        users_dishes[chat_id].append(re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", message.text.lower())))
        print(re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", message.text.lower())))
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
            users_poll_options[chat_id] = all_food_devices[:11] + ["пропуск"]
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
            bot.send_message(chat_id,
                             "Введите ингредиент в формате\nназвание количество единица_измерения,\nназвание количество единица_измерения,\n...")
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
        users_dishes[chat_id].append(re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", message.text.lower())))
        print(re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", message.text.lower())))
        bot.set_state(message.from_user.id, DishAdderStates.ingredients_selecting, chat_id)
        bot.send_message(chat_id, "Введите ингредиент в формате\nназвание количество единица_измерения,\nназвание количество единица_измерения,\n...")

# re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", string))

    @bot.message_handler(state=DishAdderStates.ingredients_selecting)
    def ingredients_adding_handler(message):
        chat_id = message.chat.id
        text = [string.strip() for string in message.text.lower().split("\n")]
        flag_all = False
        print(text)
        users_dishes[chat_id].append({})
        for string in text:
            flag_q = False
            flag_u = False
            unit = ""
            name = ""
            quantity = 0
            unit_index = None
            quantity_index = None
            string = re.sub("\s+", " ", re.sub("[^A-Za-zа-яА-Я0-9\s]+", "", string)).split(" ")
            print(string)
            for index in range(0, len(string)):
                word = string[index]
                print(word)
                if word in all_units:
                    unit = word
                    unit_index = index
                if re.match("\d+", word) is not None:
                    quantity = int(word)
                    quantity_index = index
            string_backup = " ".join(string)
            if quantity == 0:
                bot.send_message(chat_id, f"В строке\n{string_backup}\nнет количества")
            else: flag_q = True
            if unit == "":
                bot.send_message(chat_id, f"В строке\n{string_backup}\nнет единицы измерения")
            else: flag_u = True
            if flag_q is True and flag_u is True:
                string.pop(min(unit_index, quantity_index))
                string.pop(max(unit_index, quantity_index) - 1)
                name = " ".join(string).strip()
                if name not in users_dishes[chat_id][-1].keys() and re.match("\s+$", name) is None:
                    true_unit = unit
                    for unit_original in units:
                        if unit in unit_original.alternatives.keys():
                            true_unit = unit_original
                    if name in ingredients_dict.keys():
                        if true_unit.name in ingredients_dict[name]:
                            quantity = true_unit.alternatives[unit] * quantity
                            users_dishes[chat_id][-1][name] = (quantity, true_unit.name)
                            flag_all = True
                        else:
                            flag_all = False
                            bot.send_message(chat_id, f"В строке\n{string_backup}\nединица измерения не соответствует названию")
                            users_dishes[chat_id].pop()
                            break
                    else:
                        quantity = true_unit.alternatives[unit] * quantity
                        users_dishes[chat_id][-1][name] = (quantity, true_unit.name)
                        flag_all = True
                elif name in users_dishes[chat_id][-1].keys():
                    flag_all = False
                    users_dishes[chat_id].pop()
                    bot.send_message(chat_id, f"{name[0].upper() + name[1:]} появляется в списке больше одного раза")
                    break
                else:
                    flag_all = False
                    users_dishes[chat_id].pop()
                    bot.send_message(chat_id, f"В строке\n{string_backup}\nнет названия ингредиента")
                    break
            else:
                flag_all = False
                users_dishes[chat_id].pop()
                break
        if flag_all:
            bot.set_state(chat_id, DishAdderStates.cooking_time_adding, chat_id)
            all_ingredients_strings = []
            print(users_dishes[chat_id][-1])
            for ingredient in users_dishes[chat_id][-1].keys():
                all_ingredients_strings.append(ingredient + ", " + str(users_dishes[chat_id][-1][ingredient][0]) + " " + users_dishes[chat_id][-1][ingredient][1])
            all_ingredients_strings = "\n-".join(all_ingredients_strings)
            bot.send_message(chat_id, f"Были добавлены следующие ингредиенты:\n-{all_ingredients_strings}")
            bot.send_message(chat_id, f"Введите время приготовления блюда")
        else:
            users_dishes[chat_id].pop()
            bot.send_message(chat_id, f"Начните заново")

    @bot.message_handler(state=DishAdderStates.cooking_time_adding)
    def cooking_time_adding(message):
        chat_id = message.chat.id
        try:
            cooking_time = int(message.text)
            if cooking_time > 0 and cooking_time <= 5:
                users_dishes[chat_id].append(cooking_time)
                bot.set_state(chat_id, DishAdderStates.eating_time_adding, chat_id)
                bot.send_message(chat_id, "Введите время, за которое можно съесть ваше блюдо")
            else:
                bot.send_message(chat_id, "Еда столько не готовится")
        except ValueError:
            bot.send_message(chat_id, "Попробуйте ещё раз")

    @bot.message_handler(state=DishAdderStates.eating_time_adding)
    def eating_time_adding(message):
        chat_id = message.chat.id
        try:
            eating_time = int(message.text)
            if eating_time > 0 and eating_time <= 5:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(button_yes, button_no)
                users_dishes[chat_id].append(int(message.text))
                print(*users_dishes[chat_id])
                bot.set_state(chat_id, DishAdderStates.starting, chat_id)
                all_ingredients_strings = []
                for ingredient in users_dishes[chat_id][-3].keys():
                    all_ingredients_strings.append(
                        ingredient + ", " + str(users_dishes[chat_id][-3][ingredient][0]) + " " + users_dishes[chat_id][-3][ingredient][1])
                all_ingredients_strings = "\n-".join(all_ingredients_strings)
                dish_string = (f"    Вы ввели такое блюдо:\nНазвание блюда: {users_dishes[chat_id][0]}\n"
                               f"Тип блюда: {users_dishes[chat_id][1]}\n"
                               f"Времена года: {" ".join(users_dishes[chat_id][2])}\nДевайс: {users_dishes[chat_id][3]}\n"
                               f"Ингредиенты:\n-{all_ingredients_strings}\nВремя приготовления: {users_dishes[chat_id][-2]}\nВремя съедания блюда: {users_dishes[chat_id][-1]}")
                bot.send_message(chat_id, dish_string)
                bot.send_message(chat_id, "Вы точно хотите добавить это блюдо?", reply_markup=keyboard)
                bot.set_state(chat_id, DishAdderStates.quitting, chat_id)
            else:
                bot.send_message(chat_id, "Еду столько не едят")
        except ValueError:
            bot.send_message(chat_id, "Попробуйте ещё раз")

    @bot.callback_query_handler(func=lambda call: call.data == "yes", state=DishAdderStates.quitting)
    def callback_inline(call):
        chat_id = call.message.chat.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
        dish_adder.add_d(*users_dishes[chat_id])
        if users_dishes[chat_id][3] not in all_food_devices: users_devices[chat_id].append(users_dishes[chat_id][3])
        load_all_things()
        bot.send_message(chat_id, f"Блюдо добавлено")
        bot.send_message(chat_id, "Хотите создать новое расписание или отредактировать список использованых девайсов?",
                         reply_markup=keyboard)
        bot.set_state(chat_id, DishAdderStates.starting, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data == "no", state=DishAdderStates.quitting)
    def callback_inline(call):
        chat_id = call.message.chat.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices, button_add_dish, button_delete_dish)
        bot.send_message(chat_id, "Хотите создать новое расписание или отредактировать список использованых девайсов?",
                         reply_markup=keyboard)
        bot.set_state(chat_id, DishAdderStates.starting, chat_id)

    bot.infinity_polling()

if __name__ == '__main__':
    main()