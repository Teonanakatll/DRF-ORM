from string import punctuation
from aiogram import F, types, Router, Bot
from aiogram.filters import Command

from bot.filters.chat_types import ChatTypeFilter
from gpt4.utils import cons

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words = {'кабан', 'хомяк', 'выхухоль'}

@user_group_router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    # с помощю .get_chat_administrators() - бот делает запрос на сервер и получает список администраторов
    admin_list = await bot.get_chat_administrators(chat_id)
    # посмотреть все данные и свойства полученных обьектов
    # cons(admin_list)
    # код ниже это генератор списка, как и этот x = [i for i in range(10)]
    admin_list = [
        member.user.id
        for member in admin_list
        if member.status == 'creator' or member.status == 'administrator'
    ]
    # присваиваем список создателей и администраторов в поле my_admin_list - которое обьявленно в файле my_bot и
    # используется в функции IsAdmin файла chat_types для ПРОВЕРКИ ПРАВ ПОЛЬЗОВАТЕЛЕЙ для доступа к роутеру admin_router
    bot.my_admins_list = admin_list
    if message.from_user.id in admin_list:
        await message.delete()
    # cons(admin_list)

def clean_text(text: str):
    # maketrans() - вырезает все знаки пунктуации чтобы ими не маскировали мат
    return text.translate(str.maketrans('', '', punctuation))

# отлавливает сообщения которые были отредактированы
@user_group_router.edited_message()
@user_group_router.message()
async def cleaner(message: types.Message):
    # intersection - метод множества для поиска совпадений элементов одного множества в другом
    if restricted_words.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f'{message.from_user.username}, соблюдайте порядок в чате!')
        await message.delete()
        # await message.chat.ban(message.from_user.id)