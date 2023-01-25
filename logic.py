from vkbottle import EMPTY_KEYBOARD
import random
from db import cur, conn
import sqlite3
from bot import bot
from datetime import datetime, timedelta


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
            keyboard=EMPTY_KEYBOARD
        )
    else:
        await bot.api.messages.send(
            peer_id = user_id,
            message = "Теперь вы староста этой беседы",
            random_id= random.randint(1, 100),
            keyboard=EMPTY_KEYBOARD
        )


@bot.loop_wrapper.interval(seconds=5)
async def check_deadline():
    query = ''' SELECT table_id, context, create_time, deadline_time, interval, id FROM bot_deadline '''
    try:
        deadlines = cur.execute(query).fetchall()
    except sqlite3.Error as e:
        await bot.api.messages.send(
            peer_id = 318544837,
            message = f"Ошибка в функции интервале, {e}",
            random_id = random.randint(1, 100)
        )
    else:
        if deadlines:
            for deadline in deadlines:
                chat_id = deadline[0]
                context = deadline[1]
                create_time = datetime.strptime(deadline[2], "%Y-%m-%d %H:%M:%S")
                deadline_time = datetime.strptime(deadline[3], "%Y-%m-%d %H:%M:%S")
                interval = timedelta(hours=deadline[4])
                id_deadline = deadline[5]
                message = create_message_deadline(chat_id, context, create_time, deadline_time, interval, id_deadline)

                if message:
                    await bot.api.messages.send(
                        peer_id = chat_id,
                        message = message,
                        random_id = random.randint(1, 100)
                    )


def create_message_deadline(chat_id, context, create_time: datetime, deadline_time: datetime, interval: timedelta, deadline_id):
    '''  '''
    message = None
    if (create_time) >= deadline_time:
        # сообщение "дедлайн настал"
        message = f"Дедлайн '{context}' настал"
        
        # удаление дедлайна
        query = f''' DELETE FROM bot_deadline WHERE id = {deadline_id}'''
        try:
            cur.execute(query)
            conn.commit()
        except:
            pass

    elif datetime.now() >= create_time:
        # сообщение "напоминание"
        how_long = deadline_time - datetime.now()
        message = f"Напоминание\nДо конца дедлайна '{context}' Осталось: {how_long}\n Дедлайн в {deadline_time}"
        
        # изменение ячейки в таблице : create_time += interval
        create_time += interval
        query = f''' UPDATE bot_deadline SET create_time = {create_time} WHERE id = {deadline_id}'''
        try:
            cur.execute(query)
            conn.commit()
        except:
            pass

    return message