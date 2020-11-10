import requests
from bs4 import BeautifulSoup

URL = 'https://college.ks.ua/#'
HEADER = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
          'accept': '*/*'}

dict_weak = {
    1: 'Понеділок',
    2: 'Вівторок',
    3: 'Середа',
    4: 'Четвер',
    5: "П'ятниця"
}

stick_num = {
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
}


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        return None


def get_html(url, params=None):
    r = requests.get(url, headers=HEADER, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find_all('div', class_='shedule_content')


def clean(text):
    return ' '.join(text.split())


def get_timetables(group, dayofweak):
    items = parse()
    if items:
        column_num = None
        txt_msg = f'🔸*{dict_weak[dayofweak]}*🔸\n'
        one = False
        before = True
        for item in items:
            if not 'Розклад занять' in item.find('p', class_='shedule_content__title').text:
                continue
            elif 'Розклад занять' in item.find('p', class_='shedule_content__title').text and one == True:
                continue
            table = item.find('tbody')
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if group == columns[2].text.strip():
                    column_num = 2
                elif group == columns[5].text.strip():
                    column_num = 5
                elif column_num == 2:
                    if not dict_weak[dayofweak] in columns[0].text.strip() and before:
                        continue
                    if dict_weak[dayofweak] in columns[0].text.strip():
                        if columns[1].text.split():
                            txt_msg += f'{stick_num[columns[1].text.strip()]} ' \
                                       f'*{clean(columns[2].text)}* ' \
                                       f'_{clean(columns[3].text)}_\n'
                            before = False
                    else:
                        try:
                            int(columns[0].text.strip())
                            txt_msg += f'{stick_num[columns[0].text.strip()]} ' \
                                       f'*{clean(columns[1].text)}* ' \
                                       f'_{clean(columns[2].text)}_\n'
                        except Exception:
                            break
                elif column_num == 5:
                    if not dict_weak[dayofweak] in columns[0].text.strip() and before:
                        continue
                    if dict_weak[dayofweak] in columns[0].text.strip():
                        if columns[5].text.split():
                            txt_msg += f'{stick_num[columns[4].text.strip()]} ' \
                                       f'*{clean(columns[5].text)}* ' \
                                       f'_{clean(columns[6].text)}_\n'
                        before = False
                    else:
                        try:
                            int(columns[0].text.strip())
                            txt_msg += f'{stick_num[columns[3].text.strip()]} ' \
                                       f'*{clean(columns[4].text)}* ' \
                                       f'_{clean(columns[5].text)}_\n'
                        except Exception:
                            break
                else:
                    continue
        if txt_msg:
            return txt_msg
        else:
            return None
    else:
        return 'error1'


def get_replacements(message):
    items = parse()
    if items:
        num_ = 0
        txt_msg = ''
        for item in items:
            if 'Розклад занять' in item.find('p', class_='shedule_content__title').text:
                continue
            if num_ < 2:
                txt_msg += get_zblock(item, message)
                num_ = num_ + 1
            else:
                break
        return txt_msg
    else:
        return 'Error'


def get_zblock(block, message):
    day_title = block.find('p', class_='shedule_content__title').text
    table = block.find('tbody')
    lines = table.find_all('tr')
    txt_msg = f'*{day_title}*' + '\n'
    par = True
    z_par = ''
    z_aud = ''
    for line in lines:
        columns = line.find_all('td')
        if par:
            # Пропускаем первую строчку
            if columns[0].text.strip() == 'Гр.':
                continue
            # Ищем совпадения в заменах пар
            elif str(message) in columns[0].text.strip() or \
                    str(message) in columns[2].text.strip() or \
                    str(message) in columns[3].text.strip():
                z_par += f'{stick_num[columns[1].text.strip()]} пара ' \
                         f'{columns[0].text.strip()} група ' \
                         f'{columns[2].text.strip()} на ' \
                         f'*{columns[3].text.strip()}*'
                # Если указана аудитория дописываем
                if columns[4].text.strip():
                    z_par += f' в _{columns[4].text.strip()}_\n'
                else:
                    z_par += '\n'
            # Пропуск пустых блоков в заменах пар
            elif columns[2].text.strip() == '':
                continue
            # Нахождения блока замен аудиторий и конкатенация замен пар
            elif columns[2].text.strip() == 'Заміна аудиторій':
                if z_par:
                    txt_msg += '*Заміни пар:*\n' + z_par
                else:
                    txt_msg += '*Замін пар немає*\n'
                par = False
                continue
        else:
            if columns[2].text.strip() == '':
                if z_aud:
                    txt_msg += '*Заміни аудиторій:*\n' + z_aud
                else:
                    txt_msg += '*Замін аудиторій немає*\n'
                break
            # Ищем совпадения в заменах аудиторий по первому столбцу
            elif str(message) in columns[0].text.strip() or \
                    str(message) in columns[2].text.strip():
                z_aud += f'{columns[0].text.strip()} група ' \
                         f'{stick_num[columns[1].text.strip()]} пара ' \
                         f'{columns[2].text.strip()} в ' \
                         f'*{columns[3].text.strip()}*'
            # Ищем совпадения в заменах аудиторий по второму столбцу
            elif str(message) in columns[4].text.strip() or \
                    str(message) in columns[6].text.strip():
                z_aud += f'{columns[4].text.strip()} група ' \
                         f'{stick_num[columns[5].text.strip()]} пара ' \
                         f'{columns[6].text.strip()} в ' \
                         f'*{columns[7].text.strip()}*'
    return txt_msg + '\n\n'
