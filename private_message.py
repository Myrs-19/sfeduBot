import sqlite3
import random

from vkbottle import  Keyboard, Text, EMPTY_KEYBOARD, KeyboardButtonColor, OpenLink

from bot import bot
from db import cur, conn
from MyRules import RuleCreateDeadline, RuleMenu
from keyboards import KEYBOARD_MENU, KEYBOARD_BECOME_EDITOR
from logic import ALL_ACTION
from datetime import datetime, timedelta


@bot.on.private_message(RuleMenu())
async def show_keyboard(message):
    editor_id = message.from_id
    query = f''' SELECT * FROM bot_tableeditor WHERE editor_id = {editor_id} '''

    try:
        cur.execute(query)
    except sqlite3.Error as e:
        await message.answer('Ошибка', e)
    else:  # выполняется когда не было исключений
        user = cur.fetchall()
        text = ""
        if user:
            text = "Что хотите сделать?"
            keyboard = KEYBOARD_MENU
        else:
            keyboard = KEYBOARD_BECOME_EDITOR
            text = "Вы еще не староста"

    await message.answer(text, keyboard=keyboard)


@bot.on.private_message(text="/del")
async def hand1(message):
    await message.answer("keyboard removed", keyboard=EMPTY_KEYBOARD)


@bot.on.private_message(text="Стать старостой")
async def new_editor(message):
    user_id = message.from_id
    query = f''' SELECT id_chat FROM bot_user WHERE id_vk = {user_id} ''' 

    try:
        data = cur.execute(query).fetchall() # беседы в которых есть пользователь
    except sqlite3.Error as e:
        await message.answer('Ошибка', e)
    else:
        if data: # есть ли пользователь хоть в одной беседе с ботом
            query = f''' SELECT table_id FROM bot_tableeditor WHERE editor_id = {user_id} '''
            try:
                data_editor = cur.execute(query).fetchall() # беседы для которых данный пользователь уже староста
            except sqlite3.Error as e:
                await message.answer('Ошибка', e)
            else:

                chat_ids_d = set([item[0] for item in data_editor]) # id чатов, в которых пользователь староста
                chat_ids = set([chat_id[0] for chat_id in data]) # id чатов, в которых есть пользователь с ботом
                chat_ids = list(chat_ids - chat_ids_d) # вычитаем id тех бесед, где пользователь уже староста

                if chat_ids: # если есть беседы в которых пользователь не староста
                    chats = await bot.api.request('messages.getConversationsById',
                        {
                            'peer_ids': chat_ids,
                        }
                    )

                    keyboard = Keyboard(one_time=False, inline=False)

                    for chat in chats['response']['items']:
                        chat_id = chat['peer']['id']
                        title_chat = chat['chat_settings']['title']

                        keyboard.add(Text(title_chat, payload={'text': f'{chat_id}', 'action' : 0})).row() # значение action для создания старосты

                    keyboard.add(Text('меню'), color=KeyboardButtonColor.PRIMARY)
                    await message.answer('выберете беседу', keyboard=keyboard)

                else: # пользователь во всех беседах староста
                    await message.answer('Вы уже староста во всех беседах со мной', keyboard=KEYBOARD_MENU)

        else: # нет бесед с пользователем и ботом
            await message.answer('в никакой беседе вас нет со мной , сделайте инициализацию беседы командой [/init]', keyboard=KEYBOARD_BECOME_EDITOR)


@bot.on.private_message(text="Расписание")
async def table(message):
    editor_id = message.from_id
    try:
        query = f''' SELECT table_id FROM bot_tableeditor WHERE editor_id = {editor_id}; '''
        data_chats = cur.execute(query).fetchall()
        
        query = f''' SELECT name, surname FROM bot_user WHERE id_vk = {editor_id} LIMIT 1; '''
        data_editor = cur.execute(query).fetchall()
    except sqlite3.Error as e:
        await message.answer('Ошибка', e)
    else:
        name_editor = data_editor[0][0]
        surname_editor = data_editor[0][1]

        chat_ids = [item[0] for item in data_chats]

        chats = await bot.api.request('messages.getConversationsById',
            {
                'peer_ids': chat_ids,
            }
        )

        

        keyboard = Keyboard(one_time=False, inline=False)
        for chat in chats['response']['items']:
            try:
                chat_id = chat['peer']['id']
            except:
                continue
            title_chat = chat['chat_settings']['title']
            link = "http://127.0.0.1:8000/?id_chat="+ str(chat_id) + "&id_editor=" + str(editor_id) + "&ed_name=" + name_editor + "&ed_surname=" + surname_editor
            keyboard.add(OpenLink(label=title_chat, link=link)).row()

        keyboard.add(Text('меню'), color=KeyboardButtonColor.PRIMARY)
        
        await message.answer('выберете беседу', keyboard=keyboard)


@bot.on.private_message(text="Дедлайн")
async def deadline_init(message):
    editor_id = message.from_id
    try:
        query = f''' SELECT table_id FROM bot_tableeditor WHERE editor_id = {editor_id}; '''
        data_chats = cur.execute(query).fetchall()
    except sqlite3.Error as e:
        await message.answer('Ошибка', e)
    else:

        chat_ids = [item[0] for item in data_chats]

        chats = await bot.api.request('messages.getConversationsById',
            {
                'peer_ids': chat_ids,
            }
        )

        keyboard = Keyboard(one_time=False, inline=False)
        for chat in chats['response']['items']:
            try:
                chat_id = chat['peer']['id']
            except:
                continue
            title_chat = chat['chat_settings']['title']
            keyboard.add(Text(label=title_chat, payload={'text' : chat_id, 'action' : 1})).row()
            
        keyboard.add(Text('меню'), color=KeyboardButtonColor.PRIMARY)

        await message.answer('выберете беседу', keyboard=keyboard)


@bot.on.private_message(RuleCreateDeadline())
async def deadline_create(message):
    if ALL_ACTION[1]:
        user_id = message.from_id
        if user_id in ALL_ACTION[1]:
            chat_id = ALL_ACTION[1][user_id]

            text = message.text
            text = text.split(';')
            try:
                deadline_time = datetime.strptime(text[0].strip(), '%d.%m.%y %H:%M')
            except:
                await message.answer("неверный формат даты")
            else:
                try:
                    context = text[1].strip()
                except:
                    await message.answer('вы забыли ввести название дедлайна')
                else:
                    #получаем интервал для вывода сообщения дедлайна
                    d = 24 if 'д' in text[-1] else 1
                    interval = text[-1].split()
                    interval = int(interval[0]) * d

                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # -> str
                    now = datetime.strptime(now, "%Y-%m-%d %H:%M:%S") # -> datetime
                    now = now + timedelta(hours=interval)
                    if now >= deadline_time: 
                        await message.answer("Интервал слишком большой")
                    else:
                        query = f''' INSERT INTO bot_deadline (context, deadline_time, table_id, interval, create_time) VALUES ('{context}', '{deadline_time}', '{chat_id}', '{interval}', '{now}') '''
                        
                        try:
                            cur.execute(query)
                            conn.commit()
                        except sqlite3.Error as e:
                            await message.answer(f"ошибка, {e}")
                        else:
                            await message.answer("дедлайн создан", keyboard=KEYBOARD_MENU)

                            deadline_time = datetime.strftime(deadline_time, "%H:%M %d.%m.%y")
                            message = f'''назначен новый дедлайн на {deadline_time}
                            
                            {context}'''
                            await bot.api.messages.send(
                                peer_id = chat_id,
                                message=message,
                                random_id=random.randint(1,100),
                                
                            )
                            del ALL_ACTION[1][user_id]