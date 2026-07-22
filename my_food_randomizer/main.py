from my_food_json_files import Dish, FoodType, Preference, Device, Ingredient, AddDish, DishLoader

import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime

from randomizer import WeekGenerator

bot = telebot.TeleBot("8957694347:AAFIMl1W8lkPp1JcVgd9b_rBnipFk7-x_xo")

def main():
    users = {}
    dishes = DishLoader().load_dish()
    dish_loader = DishLoader()
    dish_adder = AddDish(dish_loader.load_dish(), dish_loader.load_ingredients(), dish_loader.load_preferences(), dish_loader.load_food_types(), dish_loader.load_food_devices())
    week_gen = WeekGenerator(dishes)
    months_numbers_to_seasons = {1: "зима", 2: "зима", 3: "весна", 4: "весна", 5: "весна", 6: "лето", 7: "лето", 8: "лето", 9: "осень", 10: "осень", 11: "осень", 12: "зима"}
    polls_messages_ids = {}
    all_food_devices = []
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_callback = CallbackData("calendar", "action", "year", "month", "day")
    # keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_shedule = telebot.types.InlineKeyboardButton(text="Создать расписание", callback_data="shedule")
    button_red_devices = telebot.types.InlineKeyboardButton(text="Изменить список девайсов",
                                                            callback_data="red_devices")
    devices = DishLoader().load_food_devices()
    for device in devices:
        all_food_devices.append(device.name)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = message.chat.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices)
        if chat_id not in users.keys():
            users[chat_id] = all_food_devices
        devices = "\n-".join(users[chat_id])
        bot.reply_to(message, f"Привет!\n"
                          f"    Блюда в меню могут быть приготовлены с помощью этих девайсов:\n-{devices}\n"
                          f"Все ли эти девайсы есть у вас в наличии?\n", parse_mode="HTML", reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda call: call.data == "shedule")
    def shedule(call):
        chat_id = call.message.chat.id
        if chat_id not in users.keys():
            users[chat_id] = all_food_devices
        devices = "\n-".join(users[chat_id])
        bot.send_message(chat_id, f"    Меню будет составлено с учётом наличия этих девайсов:\n-{devices}")
        today_date = datetime.datetime.now()
        bot.send_message(chat_id,"Выберите дату окончания расписания", reply_markup=calendar.create_calendar(name=calendar_callback.prefix, year=today_date.year, month=today_date.month))

    @bot.callback_query_handler(func=lambda call: call.data == "red_devices")
    def red_devices(call):
        chat_id = call.message.chat.id
        poll_message = bot.send_poll(chat_id=chat_id, question="Выберете девайсы, которые есть у вас в наличии", options=all_food_devices, is_anonymous=False, allows_multiple_answers=True)
        polls_messages_ids[chat_id] = poll_message.message_id

    @bot.poll_answer_handler()
    def handle_poll(poll):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices)
        chat_id = poll.user.id
        selected_options_ids = poll.option_ids
        selected_devices = []
        for option_id in selected_options_ids:
            selected_devices.append(all_food_devices[option_id])
        print(selected_devices)
        users[chat_id] = selected_devices
        devices = "\n-".join(selected_devices)
        bot.stop_poll(chat_id=chat_id, message_id=polls_messages_ids[chat_id])
        bot.send_message(chat_id, f"Выбраны девайсы:\n-{devices}", reply_markup=keyboard)


    @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
    def callback_inline(call: types.CallbackQuery):
        chat_id = call.from_user.id
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(button_shedule, button_red_devices)
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
                for device in users[chat_id]:
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

    bot.infinity_polling()

if __name__ == '__main__':
    main()