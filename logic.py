import random
import re
import sqlite3

from vkbottle import EMPTY_KEYBOARD
from datetime import datetime, timedelta, date

from db import cur, conn
from bot import bot
from keyboards import KEYBOARD_BECOME_EDITOR, KEYBOARD_MENU


ALL_ACTION ={
    1 : {}, # KEY - user_id, value - user_id
}

async def create_editor(chat_id, user_id):
    query = f'''INSERT INTO bot_tableeditor (editor_id, table_id) VALUES ({user_id}, { int(chat_id) });'''
    try:
        cur.execute(query)
        conn.commit()
    except sqlite3.Error as e:
        await bot.api.messages.send(
            peer_id = user_id,
            message = f"Ошибка создания старосты, {e}",
            random_id= random.randint(1, 100),
            keyboard=KEYBOARD_BECOME_EDITOR
        )
    else:
        await bot.api.messages.send(
            peer_id = user_id,
            message = "Теперь вы староста этой беседы",
            random_id= random.randint(1, 100),
            keyboard=KEYBOARD_MENU
        )


def create_message_deadline(chat_id, context, create_time: datetime, deadline_time: datetime, interval: timedelta, deadline_id):
    ''' 

    '''
    message = None
    now = datetime.now()
    if (create_time) >= deadline_time or now >= deadline_time:
        # сообщение "дедлайн настал"
        message = f'''Дедлайн настал
        
{context}'''
        
        # удаление дедлайна
        query = f''' DELETE FROM bot_deadline WHERE id = {deadline_id}'''
        try:
            cur.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            print('ERROR SQL', e)

    elif now >= create_time:
        # сообщение "напоминание"
        how_long = deadline_time - now
        how_long = get_how_long( str(how_long) )
        deadline_time = datetime.strftime(deadline_time, "%H:%M %d.%m.%y")
        message = f'''Напоминание

{context} 

До конца дедлайна осталось: {how_long}
Дедлайн в {deadline_time}'''
        
        # изменение ячейки в таблице : create_time += interval
        create_time += interval
        query = f''' UPDATE bot_deadline SET create_time = '{create_time}' WHERE id = {deadline_id}'''
        try:
            cur.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            print('ERROR SQL', e)

    return message


def get_how_long(how_long: str) -> str:

    # ищем подстроку 'чч:мм' в переданной строке
    # \d - цифра, {min, max} минимальное количество и максимальное (в данном случае цифр)
    s = re.search(r"\d{1,2}:\d{1,2}", how_long).group()

    # ищем подстроку 'кол-во_дней days' - кол-во дней не определенно, поэтому {min, } 
    # минимальное кол-во задано, а максимального нет, то есть сколько угодно цифр может быть перед ' days'
    s_d = re.search(r"\d{1,} days, ", how_long)
    
    #если день один, то в строке вместо days будет day
    if not s_d:
        s_d = re.search(r"\d{1,} day, ", how_long)
    # если подстроки с днями не было найдено, то метод возвратит NoneType
    # если подстроку с днями нашлась, то метод group в данном случае возвращает найденную подстроку 
    s_d = s_d.group() if s_d else s_d
    s = s_d + s if s_d else s

    return s


def isVisokos(year):
    '''
    это функция призвана устанавливать факт, является ли год високосным
    если да, то в году будет 366 дней вместо привычных 365
    '''
    if not year % 4:
        if not year % 100:

            if not year % 400:
                return True  # год делиться кратен 100 и без остатка делиться на 400 (вискокосный)
            else:
                return False  # год кратен 100, но на 400 без остатка разделён быть не может (невискокосный)

        else:
            return True  # год кратен 4, но на 100 без остатка не делиться (високосный)
    else:
        return False  # год не делиться без остатка на 4 (невисокосный)



def offsetMonthFunction(month, year):
    '''
    нахождение смещения месяца
    функция принимает числовое значение int
    возвращает так же int
    '''
    if 1 == month:  # месяц январь
        return 0

    elif 2 == month:  # месяц февраль
        return 31

    elif 3 == month:  # месяц март
        return 59 + isVisokos(year)

    elif 4 == month:  # месяц апрель
        return 90 + isVisokos(year)

    elif 5 == month:  # месяц май
        return 120 + isVisokos(year)

    elif 6 == month:  # месяц июль
        return 151 + isVisokos(year)

    elif 7 == month:  # месяц июль
        return 181 + isVisokos(year)

    elif 8 == month:  # месяц август
        return 212 + isVisokos(year)

    elif 9 == month:  # месяц сентябрь
        return 243 + isVisokos(year)

    elif 10 == month:  # месяц октябрь
        return 273 + isVisokos(year)

    elif 11 == month:  # месяц ноябрь
        return 304 + isVisokos(year)

    else:  # месяц декабрь
        return 334 + isVisokos(year)


def offsetYearFunction(year):
    '''
    ниже определённая функция нужна для нахождения смещения номера дня от 2023 года
    прибавляет только смещение полученное от текущего года до 2023 (текущий месяц с днём не учитываются)
    функция принимает значения типа int
    возвращает так же int
    из параметров принимает: 1) текущий год (он нужен непосредственно для вычислений), 2) смещение номера дня
    от 2023 года, которое в данный момент равно нулю. Потом функция возвращает вычисленное учитывающее только прошедшие года
    значение смещение дня от 2023 года
    '''
    offsetYear = year - 2023  # нахождение разницы в годах
    valueOfOffsetYearsForIterations = 0  # значение смещения, увеличивающееся с каждой итерацией

    while offsetYear:
        # прибавление годового смещения. Функция isVisokos принимает параметр "текущий год минус один",
        # потому что на високосность должны проверятся только предыдущие года до 2023 (не включая текущий!)
        # в году 365 дней, но в высокосном на один день больше, что учитывается
        valueOfOffsetYearsForIterations += 365 + isVisokos(year - 1)

        # проход каждого года до 2023
        offsetYear -= 1

        # нужно, чтобы каждый год до 2023 должен будет проверяться на високосность
        year -= 1

    return valueOfOffsetYearsForIterations


def fUpperOrLowerWeek():
    '''
    функция возвращает 0 (нижняя недель) или 1 (верхняя неделя)
    daysFrom2023 - смещение номера дня от 2023
    Для работы функции было решено перевести текущую дату в "номер дня", отсчёт которого начинается с 2023 года"
    например:
    для 1 января 2023 года daysFrom2023 будет равен 1;
    1 февраля 2023 года - daysFrom2023 = 32;
    1 января 2024 года - daysFrom2023 = 366;
    3 марта 2024 года - daysFrom2023 = 426;
    '''
    presentDay = date.today()  # сегодняшняя дата (например, 2023-01-31)
    # конвертируем datetime объект в строку вида Year-Month-Day, используя метод, присваиваем эти значения
    # соответствующим им переменным
    year, month, day = (int(i) for i in str(presentDay).split("-"))

    daysFrom2023 = offsetYearFunction(year) + offsetMonthFunction(month, year) + day
    return (daysFrom2023 + 5) // 7 % 2


def get_info_para(current_time):
    '''
    функция выдаёт информацию о текущей паре
    возвращает кортеж: номер пары, день недели
    '''
    # это переменные хранящие время пар (para_x - хранит время начала пары номер x)
    # все переменные - объекты datetime
    para_1start = datetime.strptime('8:00:00', '%H:%M:%S').time()
    para_1end = datetime.strptime('09:35:00', '%H:%M:%S').time()

    para_2start = datetime.strptime('9:50:00', '%H:%M:%S').time()
    para_2end = datetime.strptime('11:25:00', '%H:%M:%S').time()

    para_3start = datetime.strptime('11:55:00', '%H:%M:%S').time()
    para_3end = datetime.strptime('13:30:00', '%H:%M:%S').time()

    para_4start = datetime.strptime('13:45:00', '%H:%M:%S').time()
    para_4end = datetime.strptime('15:20:00', '%H:%M:%S').time()

    para_5start = datetime.strptime('15:50:00', '%H:%M:%S').time()
    para_5end = datetime.strptime('17:25:00', '%H:%M:%S').time()

    para_6start = datetime.strptime('17:40:00', '%H:%M:%S').time()
    para_6end = datetime.strptime('19:15:00', '%H:%M:%S').time()

    para_7start = datetime.strptime('19:30:00', '%H:%M:%S').time()
    para_7end = datetime.strptime('21:05:00', '%H:%M:%S').time()

    # этот блок условий возвращает номер текущей пары
    if para_1start <= current_time <= para_1end:
        current_para = 1

    elif para_2start <= current_time <= para_2end:
        current_para = 2

    elif para_3start <= current_time <= para_3end:
        current_para = 3

    elif para_4start <= current_time <= para_4end:
        current_para = 4

    elif para_5start <= current_time <= para_5end:
        current_para = 5

    elif para_6start <= current_time <= para_6end:
        current_para = 6

    elif para_7start <= current_time <= para_7end:
        current_para = 7

    else:
        current_para = 0  # в данный момент нету пар

    day_of_week = datetime.now().weekday() + 1 # переменная хранит день недели от Понедельника (значение 1) до Воскресенья (значение 7)

    return current_para, day_of_week
