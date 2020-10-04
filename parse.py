import requests
from bs4 import BeautifulSoup


URL = 'https://college.ks.ua/#'
HEADER = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0',
          'accept': '*/*'}

dict_weak = {1: 'Понеділок',
             2: 'Вівторок',
             3: 'Середа',
             4: 'Четвер',
             5: "П'ятниця"}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADER, params=params)
    return r


def get_content(html, group, sought, dayofweak):
    global txt_msg
    txt_msg = ''
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='shedule_content')
    if sought == 'Replacements':
        return get_replacements(items, group)
    elif sought == 'Timetable':
        return get_timetables(items, group, dayofweak)


def get_timetables(items, group, dayofweak):
    column_num = None
    txt_msg = f'🔸*{dict_weak[dayofweak]}*🔸\n'
    one = False
    before = True
    for item in items:
        if not'Розклад занять' in item.find('p', class_='shedule_content__title').text:
            continue
        elif 'Розклад занять' in item.find('p', class_='shedule_content__title').text and one == True:
            continue
        table = item.find('tbody')
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if columns[2].text.strip() == group:
                column_num = 2
            elif columns[5].text.strip() == group:
                column_num = 5
            elif column_num == 2:
                if not dict_weak[dayofweak] in columns[0].text.strip() and before:
                    continue
                if dict_weak[dayofweak] in columns[0].text.strip():
                    if columns[2].text.split():
                        txt_msg = txt_msg + f'{change_num(columns[1].text.strip())} *' + ' '.join(columns[2].text.split()) + '* _' + ' '.join(columns[3].text.split()) + '_\n'
                        before = False
                else:
                    try:
                        int(columns[0].text.strip())
                        txt_msg = txt_msg + f'{change_num(columns[0].text.strip())} *' + ' '.join(columns[1].text.split()) + '* _' + ' '.join(columns[2].text.split()) + '_\n'
                    except Exception:
                        break
            elif column_num == 5:
                if not dict_weak[dayofweak] in columns[0].text.strip() and before:
                    continue
                if dict_weak[dayofweak] in columns[0].text.strip():
                    if columns[5].text.split():
                        txt_msg = txt_msg + f'{change_num(columns[4].text.strip())} *' + ' '.join(
                            columns[5].text.split()) + '* _' + ' '.join(columns[6].text.split()) + '_\n'
                    before = False
                else:
                    try:
                        int(columns[0].text.strip())
                        txt_msg = txt_msg + f'{change_num(columns[3].text.strip())} *' + ' '.join(
                            columns[4].text.split()) + '* _' + ' '.join(columns[5].text.split()) + '_\n'
                    except Exception:
                        break
            else:
                continue
    if txt_msg:
        return txt_msg
    else:
        return None


def get_replacements(items, group):
    txt_msg = ''
    num_ = 0
    for item in items:
        if 'Розклад занять' in item.find('p', class_='shedule_content__title').text:
            continue
        if num_ < 2:
            txt_msg = txt_msg + get_zblock(item, group)
            num_ = num_ + 1
        else:
            break
    return txt_msg


def get_zblock(block, group):
    day_title = block.find('p', class_='shedule_content__title').text
    table = block.find('tbody')
    lines = table.find_all('tr')
    txt_msg = f'*{day_title}*' + '\n'
    for line in lines:
        columns = line.find_all('td')
        if columns[0].text.strip() == 'Гр.':
            continue
        if columns[0].text.strip() != str(group):
            continue
        if columns[0].text.strip() == '':
            break
        txt_msg = txt_msg + f'{change_num(columns[1].text.strip())} пара {columns[2].text.strip()} на *{columns[3].text.strip()}*'
        if columns[4].text.strip():
            txt_msg = txt_msg + f' в _{columns[4].text.strip()}_\n'
        else:
            txt_msg = txt_msg + '\n'
    return txt_msg + '\n'


def parse(group, sought, dayofweak):
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text, group, sought, dayofweak)
    else:
        print('Error')


def change_num(num):
    if num == '1':
        num = '1️⃣'
    elif num == '2':
        num = '2️⃣'
    elif num == '3':
        num = '3️⃣'
    elif num == '4':
        num = '4️⃣'
    elif num == '5':
        num = '5️⃣'
    elif num == '6':
        num = '6️⃣'
    elif num == '7':
        num = '7️⃣'
    elif num == '8':
        num = '8️⃣'
    return num

