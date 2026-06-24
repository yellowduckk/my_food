from my_food_randomizer.dish_classes import FoodDevice, Preference
from my_food_randomizer.load_dishes import load_dish
from my_food_randomizer.randomizer import WeekGenerator
import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import datetime

bot = telebot.TeleBot("8957694347:AAFIMl1W8lkPp1JcVgd9b_rBnipFk7-x_xo")

def main():
    users = {}
    dishes = load_dish()
    week_gen = WeekGenerator(dishes)
    months_numbers_to_seasons = {1: "зима", 2: "зима", 3: "весна", 4: "весна", 5: "весна", 6: "лето", 7: "лето", 8: "лето", 9: "осень", 10: "осень", 11: "осень", 12: "зима"}
    all_food_devices = []
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_callback = CallbackData("calendar", "action", "year", "month", "day")
    for device in FoodDevice:
        all_food_devices.append(device.value)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = message.chat.id
        if chat_id not in users.keys():
            users[chat_id] = all_food_devices
        devices = "\n-".join(users[chat_id])
        bot.reply_to(message, f"Привет!"
                              f"\nПропиши команду <b>[/shedule]</b>, чтобы составить расписание на неделю\n"
                              f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n-{devices}\n"
                              f"Все ли эти девайсы есть у вас в наличии?\n"
                              f"Если нет, пропишите команду \n<b>[/red_devices девайс девайс девайс]</b> в таком формате, вписывая названия девайсов,"
                              f" которых у вас нет\n", parse_mode="HTML")
        # users[chat_id] = ["духовка", "плита", "аэрогриль", "холодильник", "микроволновка", "мультиварка"]


    @bot.message_handler(commands=['shedule'])
    def shedule(message):
        chat_id = message.chat.id
        if chat_id not in users.keys():
            users[chat_id] = all_food_devices
        devices = "\n-".join(users[chat_id])
        # for device in users[chat_id]:
        #     all_food_devices = all_food_devices + "-" + device + "\n"
        bot.send_message(chat_id, f"Меню будет составлено с учётом наличия этих девайсов:\n-{devices}")
        today_date = datetime.datetime.now()
        bot.send_message(chat_id,"Выберите дату окончания расписания", reply_markup=calendar.create_calendar(name=calendar_callback.prefix, year=today_date.year, month=today_date.month))

    @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
    def callback_inline(call: types.CallbackQuery):
        chat_id = call.from_user.id
        today_date = datetime.datetime.now()
        name, action, year, month, day = call.data.split(calendar_callback.sep)
        # print(calendar_callback, calendar_callback.prefix, name, action, year, month, day)
        date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == "DAY":
            if date > today_date:
                bot.send_message(chat_id, f"Выбрана дата {date.strftime('%d.%m.%Y')}", reply_markup=types.ReplyKeyboardRemove())
                days_to_date = (date - today_date).days + 2
                months_to_date = (date.year - today_date.year) * 12 + date.month - today_date.month
                seasons = set()
                for month in range(today_date.month, months_to_date + 1):
                    seasons.add(months_numbers_to_seasons[month])
                seasons = list(seasons)
                preferences = []
                if seasons:
                    for season in seasons:
                        preferences.append(Preference(season))
                else:
                    preferences = [Preference(months_numbers_to_seasons[date.month])]
                food_devices = []
                for device in users[chat_id]:
                    food_devices.append(FoodDevice(device))
                list_of_food = week_gen.get_shedule(days_to_date, food_devices, preferences)
                print(list_of_food)
                print(days_to_date)
                bot.send_message(chat_id, list_of_food)
            elif date == today_date:
                food_devices = []
                for device in users[chat_id]:
                    food_devices.append(FoodDevice(device))
                preferences = [Preference(months_numbers_to_seasons[date.month])]
                list_of_food = week_gen.get_shedule(1, food_devices, preferences)
                bot.send_message(chat_id, list_of_food)
            else:
                bot.send_message(chat_id, "Нельзя выбрать эту дату", reply_markup=types.ReplyKeyboardRemove())
        elif action == "CANCEL":
            bot.send_message(chat_id, "Выбор даты отменён", reply_markup=types.ReplyKeyboardRemove())



        # list_of_food = wg.get_shedule(7, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))
        # raspisanie = ""
        # for food_type in list_of_food:
        #     for food in food_type:
        #         raspisanie = raspisanie + food.name + "\n"
        #     # print(*food, sep="\n")
        #     # print("----")
        # bot.send_message(message.chat.id, raspisanie)

    @bot.message_handler(commands=['red_devices'])
    def red_devices(message):
        devices_to_redact = message.text.split(' ')[1:]
        chat_id = message.chat.id
        removed_devices = []
        if chat_id not in users.keys():
            users[chat_id] = all_food_devices
        for device in devices_to_redact:
            if device in users[chat_id]:
                users[chat_id].remove(device)
                removed_devices.append(device)
        removed_devices = "\n-".join(removed_devices)
        if removed_devices:
            bot.send_message(chat_id, f"Редактирование завершено,\n"
                                              f"убраны девайсы:\n"
                                              f"-{removed_devices}\n")
        else:
            bot.send_message(chat_id, "Редактирование завершено, ничего не изменилось")



    # @bot.callback_query_handler(func=lambda call: call.data == "yes")
    # def callback_yes(call):
    #     message = call.message
    #     bot.send_message(message.chat.id, "Круто")
    #     bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
    #                           text=f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n{all_food_devices}Все ли эти девайсы есть у вас в наличии?")
    #
    #
    # @bot.callback_query_handler(func=lambda call: call.data == "no")
    # def callback_yes(call):
    #     message = call.message
    #     bot.send_message(message.chat.id, "Не круто")
    #     bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
    #                           text=f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n{all_food_devices}Все ли эти девайсы есть у вас в наличии?")



    bot.infinity_polling()

if __name__ == '__main__':
    main()