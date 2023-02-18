
from vkbottle import Keyboard, Text

KEYBOARD_MENU = Keyboard(one_time=False, inline=False)
KEYBOARD_MENU.add(Text('Стать старостой')).row()
KEYBOARD_MENU.add(Text('Расписание'))
KEYBOARD_MENU.add(Text('Дедлайн'))


KEYBOARD_BECOME_EDITOR = Keyboard(one_time=False, inline=False).add(Text('Стать старостой'))