import telebot
from telebot import types
import emoji
import requests
import gspread
import time
import pickle

f = open('token.dat', 'rb')
token = pickle.load(f)
f.close()
bot = telebot.TeleBot(token)
gc = gspread.service_account(filename='litclothesbot.json') # Json-файл с данными для сервисного аккаунта Google
sh = gc.open_by_url('link') # Ссылка на таблицу
worksheet2 = sh.worksheet("Users") # БД с id пользователей для статистики
bot.send_message(admin_id, "@lit_clothes_bot снова активен!") # admin_id - мой id в Telegram
# При сбоях и перезапуске бот мне отправляет сообщение
f = open('temporary_data.dat', 'wb')
pickle.dump({},f)
f.close()


def error(text, details=None):
    bot.send_message(admin_id, ("В работе @lit_clothes_bot произошёл сбой:\n\n" + text))
    if details:
        bot.send_message(admin_id, ("Отчёт:\n\n" + details))


def temporary_data_write(data, type_, id_):
    id_ = str(id_)
    t_data = temporary_data_read(id_, notification=False)
    if type_ == 'name':
        t_data[id_] = [{'name': data, 'type': None, 'temp': []}, False, []]
    elif type_ == 'del':
        if data is None:
            t_data[id_][2] = []
        else:
            if t_data == {}:
                t_data[id_] = [{'name': None, 'type': None, 'temp': []}, False, []]
            t_data[id_][2].append(data)
    elif t_data != {}:
        if type_ == 'clean':
            t_data[id_] = [{'name': None, 'type': None, 'temp': []}, False, []]
        else:
            t_data[id_][0][type_] = data
    else:
        bot.send_message(id_, text='*Произошла ошибка!*\nПопробуйте добавить одежду заново.',
                         parse_mode="Markdown")
    f = open('temporary_data.dat', 'wb')
    pickle.dump(t_data, f)
    f.close()


def temporary_data_read(id_, type_=False, notification=True):
    id_ = str(id_)
    f = open('temporary_data.dat', 'rb')
    t_data = pickle.load(f)
    f.close()
    if id_ in t_data:
        if type_ == 'del':
            return t_data[id_][2]
        elif type_:
            return t_data[id_][0][type_]
    if type_:
        if notification:
            bot.send_message(id_, text='*Произошла ошибка!*\nПопробуйте добавить одежду заново.',
                             parse_mode="Markdown")
        return {}
    return t_data


def find_empty_row(w_s_name):
    values_list = w_s_name.col_values(1)
    return len(values_list) + 1


def open_clothes(key):
    cell = worksheet2.findall(str(key))
    if cell == []:  # Проверяет наличие пользователя в БД с пользователями
        row = find_empty_row(worksheet2)
        date = time.localtime()[:6]
        date = list(map(str, date))
        date = ".".join(date[2::-1]) + " " + ":".join(date[3:6])  # Привожу дату в вид гггг:мм:дд чч:мм:сс
        worksheet2.update('A%s:B%s' % (row, row), [[str(key), date]])
        sh.duplicate_sheet(dheet_id, new_sheet_name = str(key))
        return []
    worksheet = sh.worksheet(str(key))
    list_of_lists = worksheet.get_all_values()
    all_cl = []
    for i in range(1, len(list_of_lists)):
        el = list_of_lists[i]
        if el[1] == 'jacket':
            all_cl.append({'name': el[0], 'type': el[1], 'temp': (el[2], el[4], el[3])})
        else:
            all_cl.append({'name': el[0], 'type': el[1], 'temp': (el[2], el[3])})
    return all_cl


def check_keybord(id_, *args):  # Добавление дополнительных кнопок с помощью необязательных аргументов
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    for extra_button in args:
        keyboard.add(extra_button)
    keyboard.add('Добавить одежду')
    cl_list = open_clothes(id_)
    if cl_list != []:
        keyboard.row('Удалить одежду', 'Что мне надеть?', 'Моя одежда')
    return keyboard


def buttons_temp(message, text_):
    # Выбор подходящей температуры для одежды
    keyboard2 = types.InlineKeyboardMarkup()
    for i in range(-35, 30, 15):
        key_1 = types.InlineKeyboardButton(text=str(i), callback_data='temp_' + str(i), )
        key_2 = types.InlineKeyboardButton(text=str(i + 5), callback_data='temp_' + str(i + 5))
        key_3 = types.InlineKeyboardButton(text=str(i + 10), callback_data='temp_' + str(i + 10))
        keyboard2.row(key_1, key_2, key_3)  # Добавление кнопок рядами по 3
    s_1 = bot.send_message(message.chat.id, text=text_, reply_markup=keyboard2, parse_mode="Markdown")
    temporary_data_write(s_1.message_id, 'del', message.chat.id)


def buttons_type(message):
    bad_names = {'что мне надеть?', 'добавить одежду', 'удалить одежду', 'моя одежда', '/help', '/start',
                 '/add_clothes', '/delete_clothes', '/instruction', '/my_clothes', '/commands'}
    bad_names |= set('\_*`#()')
    dt = open_clothes(message.from_user.id)
    bad_names |= set([dt[i]['name'] for i in range(len(dt))])
    if message.text.lower() in ('отмена', 'отмени', '/cancel', 'отменить'):
        bot.send_message(message.from_user.id, text='Хорошо, действие отменено')
        return None
    elif {message.text.lower()} & bad_names:
        bot.send_message(message.from_user.id, text='*Пожалуйста, придумайте другое название.*\n\
Чтобы добавить одежду заново, введите команду /add\_clothes или нажмите кнопку под полем ввода сообщения',
                         parse_mode="Markdown")
        return None
    name = message.text.lower()  # Мне нужно сохранять промежуточные данные до записи в БД
    temporary_data_write(name, 'name', message.from_user.id)

    keyboard_1 = types.InlineKeyboardMarkup()
    key_1 = types.InlineKeyboardButton(text='Шапка', callback_data='type_cap')
    keyboard_1.add(key_1)
    key_2 = types.InlineKeyboardButton(text='Шляпа/Кепка', callback_data='type_hat')
    keyboard_1.add(key_2)

    keyboard_2 = types.InlineKeyboardMarkup()
    key_3 = types.InlineKeyboardButton(text='Джинсы/Брюки/Шорты', callback_data='type_jeans')
    keyboard_2.add(key_3)
    key_4 = types.InlineKeyboardButton(text='Футболка/Рубашка', callback_data='type_shirt')
    keyboard_2.add(key_4)
    key_5 = types.InlineKeyboardButton(text='Куртка', callback_data='type_jacket')
    keyboard_2.add(key_5)
    key_6 = types.InlineKeyboardButton(text='Дождевик', callback_data='type_rain_jacket')
    keyboard_2.add(key_6)
    key_7 = types.InlineKeyboardButton(text='Свитер/Худи/Толстовка/Свитшот',
                                       callback_data='type_sweater')  # Для удобства считаю, что это одно и то же
    keyboard_2.add(key_7)

    keyboard_3 = types.InlineKeyboardMarkup()
    key_8 = types.InlineKeyboardButton(text='Ботинки', callback_data='type_shoes')
    keyboard_3.add(key_8)
    key_9 = types.InlineKeyboardButton(text='Сапоги', callback_data='type_boots')
    keyboard_3.add(key_9)

    keyboard_4 = types.InlineKeyboardMarkup()
    key_10 = types.InlineKeyboardButton(text='Шарф', callback_data='type_scarf')
    keyboard_4.add(key_10)
    key_11 = types.InlineKeyboardButton(text='Перчатки/Варежки', callback_data='type_gloves')
    keyboard_4.add(key_11)
    key_12 = types.InlineKeyboardButton(text='Другой вариант', callback_data='type_another')
    keyboard_4.add(key_12)

    s_1 = bot.send_message(message.from_user.id,
                           text='Выберите наиболее подходящую категорию из предложенных ниже и нажмите на неё.')
    s_2 = bot.send_message(message.from_user.id, text='Головные уборы: ', reply_markup=keyboard_1)
    s_3 = bot.send_message(message.from_user.id, text='Верхняя и нижняя одежда: ', reply_markup=keyboard_2)
    s_4 = bot.send_message(message.from_user.id, text='Обувь: ', reply_markup=keyboard_3)
    s_5 = bot.send_message(message.from_user.id, text='Другое: ', reply_markup=keyboard_4)
    temporary_data_write(s_1.message_id, 'del', message.chat.id)
    temporary_data_write(s_2.message_id, 'del', message.chat.id)
    temporary_data_write(s_3.message_id, 'del', message.chat.id)
    temporary_data_write(s_4.message_id, 'del', message.chat.id)
    temporary_data_write(s_5.message_id, 'del', message.chat.id)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Проверка какие команды досупны пользователю
    keyboard_s = check_keybord(message.chat.id)
    bot.reply_to(message,
                 "Здравствуйте, %s!\n\nФункция /instruction подскажет вам, что может делать этот бот"
                 % message.from_user.first_name, reply_markup=keyboard_s)


@bot.message_handler(commands=['instruction', 'help'])
def send_instruction(message):
    instruction_text = open('instruction.txt', 'r', encoding="utf-8").read()
    bot.send_message(message.from_user.id, text=instruction_text,
                     parse_mode="MarkdownV2")


@bot.message_handler(commands=['commands'])
def send_commands(message):
    commands = open('commands.txt', 'r', encoding="utf-8").read()
    bot.reply_to(message, commands)


@bot.message_handler(commands=['add_clothes'])
def add_clothes(message):
    # Выбор названия одежды
    sent = bot.send_message(message.from_user.id, text='*Придумайте и введите название для этой одежды\.*\n\n\
*Совет:* название должно выделять этот предмет одежды среди других\.\n\
*Пример:* зелёная футболка\.\n\
\(Название одежды не должно совпадать с командами бота или содержать символы \_\*\`\#\(\)\ и др\.\)\n\
*_Если вы нажали эту команду случайно, введите команду_* /cancel *_или "отмена"\._*', parse_mode="MarkdownV2")
    bot.register_next_step_handler(sent, buttons_type)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    def del_elems(chat_id):
        del_list = temporary_data_read(chat_id, 'del')
        for elem in del_list:
            bot.delete_message(chat_id, elem)
        temporary_data_write(None, 'del', call.message.chat.id)

    if call.data[:4] != "del_":
        temp = temporary_data_read(call.message.chat.id, 'temp')
        cl_type = temporary_data_read(call.message.chat.id, 'type')
        if temp == {} or cl_type == {}:
            return None
    keys = call.message.json['reply_markup']['inline_keyboard']
    for i in range(
            len(keys)):  # Эти циклы нужны для удобства работы с кнопками, которые задаются несколькими сообщениями
        for ii in range(len(keys[i])):  # Или в несколько рядов (температура)
            if call.data == keys[i][ii]['callback_data']:
                # Для удобства пользователя в чате фиксируется его выбор
                bot.send_message(call.message.chat.id, ('''Вы выбрали *"%s"*''' % keys[i][ii]['text']),
                                 parse_mode="Markdown")
                if call.data[:5] == "type_":
                    cl_type = call.data[5:]
                    del_elems(call.message.chat.id)
                    temporary_data_write(cl_type, 'type', call.message.chat.id)
                    if cl_type == 'sweater':
                        buttons_temp(call.message, 'Выберите *минимальную* температуру, при которой вы наденете эту \
одежду, *не надевая ничего поверх* (°С) и нажмите на неё.')
                    elif cl_type == 'jacket':
                        buttons_temp(call.message,'Выберите *минимальную* температуру, при которой вы наденете эту \
куртку *без кофты или свитера* (°С) и нажмите на неё.')
                    else:
                        buttons_temp(call.message,
                                     'Выберите *минимальную* температуру, подходящую для этой одежды (°С) и нажмите на неё.')
                elif call.data[:5] == 'temp_':
                    del_elems(call.message.chat.id)
                    temp.append(int(call.data[5:]))
                    temporary_data_write(temp, 'temp', call.message.chat.id)
                    if len(temp) == 1:
                        if cl_type == 'sweater':
                            buttons_temp(call.message, 'Выберите *максимальную* температуру, при которой вы наденете \
эту одежду *без куртки* (°С) и нажмите на неё.')
                        elif cl_type == 'jacket':
                            buttons_temp(call.message, 'Выберите *максимальную* температуру, при которой вы наденете \
эту куртку (°С) и нажмите на неё.')
                        else:
                            buttons_temp(call.message,
                                         'Выберите *максимальную* температуру, подходящую для этой одежды (°С) и нажмите на неё.')
                    elif len(temp) == 2 and cl_type == 'jacket':
                        buttons_temp(call.message, 'Выберите *минимальную* температуру, при которой вы наденете \
эту куртку, *надев под неё кофту или свитер* (°С) и нажмите на неё.')
                elif call.data[:4] == "del_":
                    worksheet = sh.worksheet(str(call.message.chat.id))
                    cl_name = call.data[4:]
                    del_elems(call.message.chat.id)
                    cell_name = worksheet.findall(cl_name)
                    if cell_name != []:
                        row_num = cell_name[0].row
                    else:
                        bot.send_message(call.message.chat.id,
                                         'В работе бота произошёл сбой: выбранный предмет одежды не найден.')
                        error('Выбранный предмет одежды не найден (удаление).')
                        return None
                    list_of_lists = worksheet.get_all_values()
                    del list_of_lists[row_num - 1]
                    list_of_lists.append(['', '', '', '', ''])
                    # Чтобы оставить кол-во строк прежним (иначе последняя строка не будет обновляться)
                    worksheet.update('A1:E%s' % str(len(list_of_lists) + 1), list_of_lists)
                    keyboard_s = check_keybord(call.message.chat.id)
                    bot.send_message(call.message.chat.id, 'Хорошо, одежда удалена', reply_markup=keyboard_s)
                    return None

    if (len(temp) > 1 and cl_type != 'jacket') or len(temp) > 2:
        temp.sort()  # На случай, если пользователь ввёл температуру в неправильном порядке
        # Данные в таблице выглядят как [[],[],[]...], поэтому я передаю их в таком виде
        worksheet = sh.worksheet(str(call.message.chat.id))
        row = find_empty_row(worksheet)
        name = temporary_data_read(call.message.chat.id, 'name')
        temporary_data_write(None, 'clean', call.message.chat.id)  # Стираю временные данные
        if len(temp) > 2:
            cl = [[name, cl_type, temp[0], temp[-1], temp[1]]]
            worksheet.update(('A%s:E%s' % (str(row), str(row))), cl)
        else:
            cl = [[name, cl_type, temp[0], temp[1]]]
            worksheet.update(('A%s:D%s' % (str(row), str(row))), cl)
        keyboard_s = check_keybord(call.message.chat.id)
        bot.send_message(call.message.chat.id, '''Вы добавили *"%s"*, можно надевать при температуре *%s*.'''
                         % (name, 'от ' + str(temp[0]) + '°С до ' + str(temp[-1]) + '°С'), reply_markup=keyboard_s,
                         parse_mode="Markdown")
        del temp


@bot.message_handler(commands=['delete_clothes'])
def delete_clothes(message):
    def del_butts(message):
        if message.text.lower() in ('отмена', 'отмени', '/cancel', 'отменить'):
            bot.edit_message_reply_markup(message.from_user.id, message.message_id - 1)
            bot.delete_message(message.from_user.id, message.message_id - 1)
        get_text_messages(message)

    cl_list = open_clothes(message.chat.id)
    if len(cl_list) == 0:
        bot.send_message(message.from_user.id, text='Вы ещё не добавили одежду.\n\
Чтобы добавить одежду, введите команду /add_clothes или нажмите кнопку под полем ввода сообщения')
        return None
    names = []
    f_names = []
    for elem in cl_list:
        cl_name = elem['name']
        names.append(cl_name)
        f_names.append(cl_name)
    keyboard_cl = types.InlineKeyboardMarkup()
    for i in range(len(names)):
        exec('''key_cl_%s = types.InlineKeyboardButton(text="%s", callback_data="del_%s")''' % (
            str(i), names[i], f_names[i]))
        exec('''keyboard_cl.add(key_cl_%s)''' % str(i))
    sent = bot.send_message(message.from_user.id, text='*Выбирите одежду, которую вы хотите удалить в списке ниже \
и нажмите на неё.*\nЕсли вы нажали эту команду случайно или передумали, введите команду /cancel или "отмена"',
                            reply_markup=keyboard_cl, parse_mode="Markdown")
    temporary_data_write(sent.message_id, 'del', message.chat.id)
    bot.register_next_step_handler(sent, del_butts)


@bot.message_handler(commands=['what_to_wear'])
def what_to_wear(message):
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard_s = check_keybord(message.chat.id, button_geo)
    if len(open_clothes(message.chat.id)) > 0:
        bot.send_message(message.chat.id, '''Для использования этой функции поделитесь местоположением, \
нажав кнопку "Отправить местоположение"''', reply_markup=keyboard_s)
    else:
        bot.send_message(message.chat.id, 'Вы ещё не добавили одежду.')


# Получаю локацию
@bot.message_handler(content_types=['location'])
def location (message):
    #Удаляю кнопку "Отправить местоположение" и проверяю клавиатуру
    keyboard_l = check_keybord(message.chat.id)
    lat = message.location.latitude
    lon = message.location.longitude
    temp = []
    rain = False
    appid = ""# id в openweathermap
    #Получение текущих погодных условий
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                    params={'lat':lat,'lon':lon, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        if 'дождь' in data['weather'][0]['description']:
            rain = True
        temp.append(data['main']['temp_min'])
        temp.append(data['main']['temp_max'])
    except Exception as e:
        error("Exception (weather): "+str(e))
        pass
    #Получение прогноза погоды
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                    params={'lat':lat,'lon':lon, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        for i in data['list']:
            if 'дождь' in i['weather'][0]['description']:
                rain = True
            if i['main']['temp'] == i['main']['temp_min']:
                # В первых 3 строках прогноза min и max разные, потом - одинаковые
                temp.append(i['main']['temp'])
            else:
                temp.append(i['main']['temp_min'])
                temp.append(i['main']['temp_max'])
    except Exception as e:
        error("Exception (forecast): "+str(e))
        pass
    bot.delete_message(message.chat.id, message.message_id)
    temp_t = (min(temp[:6]), max(temp[:6]))    #[:5] - код выше получает прогноз на 5 дней, а мне нужны только первые несколько часов
    cl_l = open_clothes(message.chat.id)         #Данные о темпреатуре загружаются парами (min, max) с интервалом 3 часа, а первая пара - данные сейчас
    cl_a = []
    sweaters_with_sth = []
    jackets_with_sth = []
    for elem in cl_l:
        min_ = int(elem['temp'][0])
        max_ = int(elem['temp'][-1])
        if elem['type'] == 'jacket':
            min_2 = int(elem['temp'][1])
            if (temp_t[1] - max_) <= 3: #Не слишком ли куртка тёплая
                if (temp_t[0] - min_2) >= -3: #Можно ли носить без всего
                    cl_a.append(elem)
                elif (temp_t[0] - min_) >= -3: #Можно ли носить с кофтами
                    jackets_with_sth.append(elem)
        elif elem['type'] == 'sweater':
            if (temp_t[1] - max_) <= 3:
                if (temp_t[0] - min_) >= -3: #Можно ли носить без куртки
                    cl_a.append(elem)
                else:
                    sweaters_with_sth.append(elem)
        else:
            if (temp_t[1] - max_) <= 3 and (temp_t[0] - min_) >= -3:
                if (elem['type'] in ('rain_jacket','boots') and rain == True) or not(elem['type'] in ('rain_jacket','boots')):
                    cl_a.append(elem)
    if rain == True:
        bot.send_message(message.from_user.id, text=('В ближайшие несколько часов температура воздуха будет в диапозоне \
*от %s°С до %s°С*, возможен дождь.'%(int(temp_t[0]),int(temp_t[1]))),reply_markup=keyboard_l, parse_mode = "Markdown")
    else: 
        bot.send_message(message.from_user.id, text=('В ближайшие несколько часов температура воздуха будет в диапозоне \
*от %s°С до %s°С*, дождя не ожидается.'%(int(temp_t[0]),int(temp_t[1]))),reply_markup=keyboard_l, parse_mode = "Markdown")
    if sweaters_with_sth != [] and jackets_with_sth != []:
        jackets = ['''*"'''+i['name']+'''"*''' for i in jackets_with_sth]
        jackets = ",\n".join(jackets)
        sweaters = ['''*"'''+i['name']+'''"*''' for i in sweaters_with_sth]
        sweaters = ",\n".join(sweaters)
        bot.send_message(message.from_user.id, text=('Вы можете надеть куртки:\n%s\nвместе с кофтами:\n%s'%(jackets,sweaters)),
            parse_mode = "Markdown", reply_markup=keyboard_l)
        bot.send_message(message.from_user.id, text=('Ещё найдено %s подходящих предметов одежды:'%len(cl_a)))
    elif cl_a != []:
        bot.send_message(message.from_user.id, text=('Найдено %s подходящих предметов одежды:'%len(cl_a)), reply_markup=keyboard_l)
    else:
        bot.send_message(message.from_user.id, text='К сожалению, мы не нашли подходящую одежду', reply_markup=keyboard_l)
    for elem in cl_a:
        bot.send_message(message.from_user.id, text=('*'+elem['name']+'*'+'\n'), parse_mode = "Markdown")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() in ('добавить одежду', 'дабавь одежду', 'добавление одежды'):
        add_clothes(message)
    elif message.text.lower() in ('удалить одежду', 'удали одежду', 'удаление одежды'):
        delete_clothes(message)
    elif message.text.lower() in ('что мне надеть', 'что мне надеть?', 'что надеть?', 'что надеть'):
        what_to_wear(message)
    elif message.text.lower() in ('мой гардероб', 'моя одежда', 'покажи мою одежду', 'покажи мой гардероб'):
        my_clothes(message)
    elif message.text.lower() in ('отмена', 'отмени', '/cancel', 'отменить'):
        keyboard_s = check_keybord(message.chat.id)
        bot.send_message(message.from_user.id, text='Хорошо, действие отменено.', reply_markup=keyboard_s)
    elif ":" in emoji.demojize(message.text):
        keyboard_s = check_keybord(message.chat.id)
        bot.send_message(message.from_user.id, emoji.emojize(':mechanical_arm:'), reply_markup=keyboard_s)
    else:
        keyboard_s = check_keybord(message.chat.id)
        bot.send_message(message.from_user.id, text='К сожалению, я пока что не умею отвечать на такие запросы.',
                         reply_markup=keyboard_s)


@bot.message_handler(content_types=['sticker'])
def get_stickres(message):
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAIJQ2ENSlCrBxHarRJU1IVzkZn_LzINAAIvAgACusCVBcIH4zCxGwpQIAQ")


def main():
    try:
        bot.polling(none_stop=False, interval=0)
    except Exception as e:
        # Если возникают эти ошибки, бот 2 минуты не отвечает, а потом опять включается
        if "requests.exceptions.ReadTimeout" in str(e):
            error('Requests', str(e))
            time.sleep(4)
        elif "Quota exceeded for quota metric 'Read requests'" in str(e):  # Превышенный лимит чтения БД в минуту
            error('Quotas', str(e))
            time.sleep(120)
            main()


main()
