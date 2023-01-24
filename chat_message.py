from bot import bot

import sqlite3

from db import cur, conn


@bot.on.chat_message(text="/init")
async def init_chat(message):

    chat_id = message.chat_id
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
                    'peer_id': 2000000000 + message.chat_id,
                    'fields': ['domain'],
                }
            )
            # список из словарей в которых данные участников беседы
            data_chat = data_chat['response']['profiles']

            values = ""
            for user in data_chat:
                values += f"({user['id']}, '{user['first_name']}', '{user['last_name']}', '{user['domain']}', {2000000000 + chat_id}),"

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
    chat_id = message.chat_id

    await message.answer('я не знаю')