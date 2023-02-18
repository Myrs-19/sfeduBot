from bot import bot
from db import cur, conn
from logic import create_message_deadline, get_message_what_is_current_les, get_info_para_and_day, is_upper_week

import sqlite3
import random

from datetime import datetime, timedelta



@bot.on.chat_message(text="/init")
async def init_chat(message):

    chat_id = message.chat_id + 2000000000
    query = f'''SELECT * FROM bot_user WHERE id_chat={chat_id} LIMIT 1;'''
    try:
        data = cur.execute(query).fetchall()
    except sqlite3.Error as e:
        await message.answer(f"Ошибка данных, {e}")
    else:
        if data:
            await message.answer("беседа уже инициализирована")
        else:
            # query = '''INSERT INTO bot_user (id, name, surname, domain, chat_id) VALUES (1, 'mike', 'sel', 'domain', 2);'''
            data_chat = await bot.api.request('messages.getConversationMembers',
                {
                    'peer_id':  chat_id,
                    'fields': ['domain'],
                }
            )
            # список из словарей в которых данные участников беседы
            data_chat = data_chat['response']['profiles']

            values = ""
            for user in data_chat:
                values += f"({user['id']}, '{user['first_name']}', '{user['last_name']}', '{user['domain']}', {chat_id}),"

            values = values[:-1]  # исключаем последнюю запятую
            query = f'''INSERT INTO bot_user (id_vk, name, surname, domain, id_chat) VALUES {values};'''
            try:
                cur.execute(query)
                conn.commit()
            except sqlite3.Error as e:
                await message.answer(f"Ошибка инициализации, {e}")
            else:
                await message.answer("беседа успешно инициализирована")


@bot.on.chat_message(text="какая сейчас пара")
async def table_right_now(message):
    ''' in developing '''
    number_para, number_day = get_info_para_and_day()
    number_week = is_upper_week()
    chat_id = message.chat_id + 2000000000

    text = get_message_what_is_current_les(
        chat_id=chat_id, 
        number_day=number_day,
        number_para=number_para,
        number_week=number_week
        )

    context = f"number_para: {number_para}; number_day: {number_day}; number_week: {number_week}"

    await message.answer(context)



# сообщение-напоминание с интевалом 5 минут
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