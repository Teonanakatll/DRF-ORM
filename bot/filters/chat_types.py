from aiogram.filters import Filter
from aiogram import Bot, types

from gpt4.utils import cons


class ChatTypeFilter(Filter):
    # фильтр принимает список чатов
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # проверяем что сообщение имеет тип чата указанный в фильтре роутера и если типы чата сообщения и
    # тип чата указанного в фильтре роутера соврпадают возвращаем значение True
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        # cons(f'my_admins_list from IsAdmin {bot.my_admins_list}')
        return message.from_user.id in bot.my_admins_list