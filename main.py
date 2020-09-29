import requests
from bs4 import BeautifulSoup
import telebot
import configs
from telebot import types
import datetime

bot = telebot.TeleBot(configs.token)

URL = 'https://college.ks.ua/#'
HEADER = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
          'accept': '*/*'}

text_msg = ''


@bot.message_handler(commands=['start', 'help', 'get_replacements'])
def commands_handler(message):
    if message.text == '/start':
        start(message)
    elif message.text == '/get_replacements':
        get_replacement(message)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == 'Узнать замены':
        get_replacement(message)


def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('Узнать замены')
    markup.add(btn1)
    bot.send_message(message.from_user.id, 'Нажмите кнопку ниже:', reply_markup=markup)


def get_html(url, params=None):
    r = requests.get(url, headers=HEADER, params=params)
    return r


def get_content(html, group):
    txt_msg = ''
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='shedule_content')
    for item in items:
        if 'Розклад занять' in item.find('p', class_='shedule_content__title').text:
            continue
        day_title = item.find('p', class_='shedule_content__title').text
        day = day_title[day_title.find('«') + 1:day_title.find('»')]
        if not datetime.datetime.today().timetuple()[2] <= int(day) < datetime.datetime.today().timetuple()[2] + 8:
            break
        txt_msg = text_msg + get_zblock(item, group)
    return txt_msg


def get_zblock(block, group):
    day_title = block.find('p', class_='shedule_content__title').text
    table = block.find('tbody')
    lines = table.find_all('tr')
    txt_msg = day_title + '\n'
    for line in lines:
        columns = line.find_all('td')
        if columns[0].text.strip() == 'Гр.':
            continue
        if columns[0].text.strip() != str(group):
            continue
        if columns[0].text.strip() == '':
            break
        txt_msg = txt_msg + f'{columns[1].text.strip()} пара {columns[2].text.strip()} на {columns[3].text.strip()}'
        if columns[4].text.strip():
            txt_msg = txt_msg + f' в {columns[4].text.strip()}\n'
        else:
            txt_msg = txt_msg + '\n'
    return txt_msg + '\n'


def parse(group):
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text, group)
    else:
        print('Error ')


def get_replacement(message):
    bot.send_message(message.from_user.id, 'Введите номер группы:')
    bot.register_next_step_handler(message, get_replacement_)


def get_replacement_(message):
    bot.send_message(message.from_user.id, parse(message.text))
    start(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)
