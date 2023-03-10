from bot import bot
from vkbottle import API, Keyboard, KeyboardButtonColor, Text, EMPTY_KEYBOARD, GroupEventType, GroupTypes, OpenLink, keyboard_gen
from vkbottle.bot import MessageEvent
import json
import random

from logic import ALL_ACTION, create_editor
from keyboards import KEYBOARD_MENU

#обработчик событий сообщений (для кнопок)
@bot.on.raw_event(GroupEventType.MESSAGE_NEW, dataclass=GroupTypes.MessageNew)
async def handle_message_event(event: MessageEvent):
    message_data = event.object.message
    try:
        meta_data = json.loads(event.object.message.payload) # -> dict
    except:
        pass
    else:
        try:
            action = meta_data['action']
        except:
            action = None
        try:
            chat_id = meta_data['text']
        except:
            chat_id=None

        user_id = message_data.from_id
        if action == 0 and 'text' in meta_data: # создание старосты
            await create_editor(chat_id, user_id)
        elif action == 1: # создание дедлайна
            ALL_ACTION[1][user_id] = chat_id # добавляем данные для будущего действия (создания дедлайна)
            await bot.api.messages.send(
                user_id=user_id, 
                message="Напишите дедлайн (Дата; название; интервал д/ч)\nДата в виде: дд.мм.гг чч:мм",
                random_id=random.randint(1, 100),
                keyboard=Keyboard(one_time=True, inline=False).add(Text('отменить', payload={'action' : 2}), color=KeyboardButtonColor.NEGATIVE),
                )
        elif action == 2:
            # удаление создания дедлайна (из словаря ALL_ACTION[1])
            try:
                del ALL_ACTION[1][user_id]
            except:
                pass
            else:
                await bot.api.messages.send(
                    user_id=user_id, 
                    message="создание прекращено",
                    random_id=random.randint(1, 100),
                    keyboard=KEYBOARD_MENU,
                )