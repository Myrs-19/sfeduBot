import random
import re
import sqlite3

from vkbottle import EMPTY_KEYBOARD
from datetime import datetime, timedelta

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