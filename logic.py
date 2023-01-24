from vkbottle import EMPTY_KEYBOARD
import random
from db import cur, conn
import sqlite3
from bot import bot


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
