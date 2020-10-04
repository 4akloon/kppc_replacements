import telebot
import configs
from telebot import types
import parse as Parse
import datetime

bot = telebot.TeleBot(configs.token)

URL = 'https://college.ks.ua/#'
HEADER = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
          'accept': '*/*'}

txt_msg = ''


@bot.message_handler(commands=['start', 'help', 'get_replacements'])
def commands_handler(message):
    if message.text == '/start':
        start(message)
    elif message.text == '/get_replacements':
        get_replacement(message)
    elif message.text == '/get_timetable':
        get_timetable1(message)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == 'Узнать замены':
        get_replacement(message)
    elif message.text == 'Узнать расписание':
        get_timetable1(message)
    else:
        start(message)


def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Узнать замены')
    btn2 = types.KeyboardButton('Узнать расписание')
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, 'Нажмите кнопку ниже:', reply_markup=markup)


def get_replacement(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Введите номер группы:', reply_markup=markup)
    bot.register_next_step_handler(message, get_replacement_)


def get_replacement_(message):
    if message.content_type == 'text':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, 'Подождите...', reply_markup=markup)
        ret = Parse.parse(message.text, 'Replacements', '')
        if ret:
            bot.send_message(message.from_user.id, ret, parse_mode="markdown")
            start(message)
        else:
            bot.send_message(message.from_user.id, 'Нет замен')
            start(message)
    else:
        bot.send_message(message.from_user.id, 'Неверный ввод')
        start(message)


def get_timetable1(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.from_user.id, 'Введите номер группы:', reply_markup=markup)
    bot.register_next_step_handler(message, get_timetable2)


def get_timetable2(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(types.KeyboardButton('Сегодня'), types.KeyboardButton('Завтра'), types.KeyboardButton('Послезавтра'))
    markup.add(types.KeyboardButton('Понедельник'))
    markup.add(types.KeyboardButton('Вторник'))
    markup.add(types.KeyboardButton('Среда'))
    markup.add(types.KeyboardButton('Четвер'))
    markup.add(types.KeyboardButton('Пятница'))
    bot.send_message(message.from_user.id, 'Введите/Выберите день недели:', reply_markup=markup)
    bot.register_next_step_handler(message, get_timetable3, message.text)


def get_timetable3(message, group):
    if message.content_type == 'text':
        cont = True
        cont_ = True
        if message.text == 'Понедельник' or message.text == 'Понеділок' or message.text == 'понедельник' or message.text == 'понеділок':
            dayofweak = 1
        elif message.text == 'Вторник' or message.text == 'вторник' or message.text == 'Вівторок' or message.text == 'вівторок':
            dayofweak = 2
        elif message.text == 'Среда' or message.text == 'среда' or message.text == 'Середа' or message.text == 'середа':
            dayofweak = 3
        elif message.text == 'Четвер' or message.text == 'четвер' or message.text == 'Четвер' or message.text == 'четвер':
            dayofweak = 4
        elif message.text == "П'ятниця" or message.text == "п'ятниця" or message.text == "пятниця" or message.text == "Пятниця" or message.text == "Пятница" or message.text == "пятница":
            dayofweak = 5
        elif message.text == 'Сегодня' or message.text == 'сегодня' or message.text == 'сьогодні' or message.text == 'Сьогодні':
            dayofweak = datetime.datetime.isoweekday(datetime.datetime.today())
        elif message.text == 'Завтра' or message.text == 'завтра':
            dayofweak = datetime.datetime.isoweekday(datetime.datetime.today()) + 1
        elif message.text == 'Післязавтра' or message.text == 'післязавтра' or message.text == 'послезавтра' or message.text == 'Послезавтра':
            dayofweak = datetime.datetime.isoweekday(datetime.datetime.today()) + 2
        else:
            bot.send_message(message.from_user.id, 'Неверный ввод')
            bot.register_next_step_handler(message, get_timetable3, group)
            cont = False
        if cont:
            if dayofweak == 6:
                dayofweak = 'В субботу нет пар)'
                cont_ = False
            elif dayofweak == 7:
                dayofweak = 'В воскресенье нет пар)'
                cont_ = False
            elif dayofweak == 8:
                dayofweak = 1
            elif dayofweak == 9:
                dayofweak = 2
            if cont_:
                markup = types.ReplyKeyboardRemove()
                bot.send_message(message.from_user.id, 'Подождите...', reply_markup=markup)
                ret = Parse.parse(group, 'Timetable', dayofweak)
                if ret:
                    bot.send_message(message.from_user.id, ret, parse_mode="markdown")
                    start(message)
                else:
                    bot.send_message(message.from_user.id, 'Неверный ввод')
                    start(message)
            else:
                markup = types.ReplyKeyboardRemove()
                bot.send_message(message.from_user.id, dayofweak, reply_markup=markup)
                start(message)
    else:
        bot.send_message(message.from_user.id, 'Неверный ввод')
        bot.register_next_step_handler(message, get_timetable3, group)


if __name__ == '__main__':
    bot.polling(none_stop=True)
