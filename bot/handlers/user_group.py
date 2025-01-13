from string import punctuation
from aiogram import F, types, Router
from bot.filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))

restricted_words = {'кабан', 'хомяк', 'выхухоль'}

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