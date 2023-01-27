from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message


class RuleCreateDeadline(ABCRule):
    async def check(self, event):
        if event.text.count(';') == 2:
            d = event.text.split(';')[2] # интервал
            return 'ч' in d or 'д' in d
        return False


class RuleMenu(ABCRule):
    async def check(self, event):
        return event.text in ['Начать', 'Меню', 'меню', 'начать']