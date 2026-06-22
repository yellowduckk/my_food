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
    keyboard = telebot.types.InlineKeyboardMarkup()
    all_food_devices = ""
    calendar = Calendar(language=RUSSIAN_LANGUAGE)
    calendar_callback = CallbackData("calendar_1", "action", "year", "month", "day")
    for device in FoodDevice:
        all_food_devices = all_food_devices + "-{}".format(device.value) + "\n"

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, f"Привет!\nПропиши команду [/shedule], чтобы составить расписание на неделю\n"
                              f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n{all_food_devices}"
                              f"Все ли эти девайсы есть у вас в наличии? Если нет, пропишите команду [/red_devices девайс девайс девайс] в таком формате, вписывая названия девайсов, которых нет у вас в наличии\n")
        users[message.chat.id] = ["духовка", "плита", "аэрогриль", "холодильник", "микроволновка", "мультиварка"]


    @bot.message_handler(commands=['shedule'])
    def shedule(message):
        chat_id = message.chat.id
        all_food_devices = ""
        for device in users[chat_id]:
            all_food_devices = all_food_devices + "-" + device + "\n"
        bot.send_message(chat_id, f"Меню будет составлено с учётом наличия этих девайсов:\n{all_food_devices}")
        now = datetime.datetime.now()
        bot.send_message(chat_id,"Выберете дату окончания расписания", reply_markup=calendar.create_calendar(name=calendar_callback.prefix, year=now.year, month=now.month))

    @bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_callback.prefix))
    def callback_inline(call: types.CallbackQuery):
        name, action, year, month, day = call.data.split(calendar_callback.sep)
        date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
        if action == "DAY":
            bot.send_message(call.from_user.id, f"Выбрана дата {date.strftime('%d.%m.%Y')}", reply_markup=types.ReplyKeyboardRemove())
        elif action == "CANCEL":
            bot.send_message(call.from_user.id, "LOL", reply_markup=types.ReplyKeyboardRemove())



        # list_of_food = wg.get_shedule(7, [FoodDevice("духовка"), FoodDevice("плита"), FoodDevice("аэрогриль"), FoodDevice("холодильник"), FoodDevice("микроволновка"), FoodDevice("мультиварка")], Preference("лето"))
        # raspisanie = ""
        # for food_type in list_of_food:
        #     for food in food_type:
        #         raspisanie = raspisanie + food.name + "\n"
        #     # print(*food, sep="\n")
        #     # print("----")
        # bot.send_message(message.chat.id, raspisanie)

    @bot.message_handler(commands=['/red_devices'])
    def red_devices(message):
        devices_to_redact = message.text.split(' ')[1:]
        chat_id = message.chat.id
        for device in devices_to_redact:
            if device in users[chat_id]:
                users[chat_id].remove(device)
        bot.send_message(message.chat.id, "Редактирование завершено")



    @bot.callback_query_handler(func=lambda call: call.data == "yes")
    def callback_yes(call):
        message = call.message
        bot.send_message(message.chat.id, "Круто")
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n{all_food_devices}Все ли эти девайсы есть у вас в наличии?")


    @bot.callback_query_handler(func=lambda call: call.data == "no")
    def callback_yes(call):
        message = call.message
        bot.send_message(message.chat.id, "Не круто")
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=f"Блюда в меню могут быть приготовлены с помощью этих девайсов:\n{all_food_devices}Все ли эти девайсы есть у вас в наличии?")



    bot.infinity_polling()

if __name__ == '__main__':
    main()