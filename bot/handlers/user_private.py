from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from bot.filters.chat_types import ChatTypeFilter
from aiogram.utils.formatting import as_list, as_marked_section, Bold


from bot.kbds import reply
from bot.kbds.reply import test_kb
from gpt4.utils import cons

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

# отслеживание события отправки сообщения
@user_private_router.message(CommandStart())
# async - позволяет обрабатывать задачи (например, получение сообщений от Telegram API) без блокировки основного потока.
async def start_smd(message: types.Message):
    # из файла с клавиатурой указываем нашу клавиатуру, если клавиатура созданна через ReplyKeyboardBuilder, то вызываем
    # метод as_markup() и передаём в него параметры
    await message.answer('Привет я виртуальный помощник!', reply_markup=reply.start_kb3.as_markup(
                                                resize_keyboard=True, input_field_placeholder='Что вас интересует?'))

# @user_private_router.message(F.text.lower() == 'меню')
# префикс '/' - в Comand() указан по умолчанию, служит для указания условия ИЛИ, чтобы в аргументе хэндлера обрабатывать
# и команду и фильтры
@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'меню')))
async def menu_cmd(message: types.Message):
    # удаляем клавиатуру при активации меню
    await message.answer('Вот меню:', reply_markup=reply.del_kbd)

mag = ['О магазине', 'о магазине']
# @user_private_router.message(or_f(Command('about'), (F.text == 'О магазине'), (F.text == 'о магазине')))
# праверяем есть ли строка в списке
@user_private_router.message(or_f(Command('about'), (F.text.in_(mag))))
# @user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    cons(message.text)
    await message.answer('О нас:')

@user_private_router.message(F.text.lower() == 'варианты оплаты')
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):

    text = as_marked_section(
        Bold('Варианты оплаты:'),
        'Картой в боте',
        'При получении карта/кеш',
        'В заведении',
        marker='💎'
    )
    await message.answer(text.as_html())
    # parse_mode=ParseMode.HTML указываем в Dispatcher()
    await message.answer('<i>Способы оплаты:</i>')                    # italic
    await message.answer('<s>Способы оплаты:</s>')                    # зачёркнутый
    await message.answer('<em>Способы оплаты:</em>')                  # italic
    await message.answer('<code>Способы оплаты:</code>')              # стиль кода
    await message.answer('<pre>Способы оплаты:</pre>')                # ответ
    await message.answer('<blockquote>Способы оплаты:</blockquote>')  # цитата с кавычками
    await message.answer('<strong>Способы оплаты:</strong>')          # bold
    await message.answer('<b>Способы оплаты:</b>')                    # bold
    await message.answer('<ins>Способы оплаты:</ins>')                # подчёркнутый

# функцию можно декорировать несколькими декораторами
@user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'варианты'))
@user_private_router.message(Command('shipping'))
async def shipping_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold('Варианты доставки/заказа:'),
            'Курьер',
            'Самовынос (сейчас прибегу заберу)',
            'Покушаю у вас (сейчас прибегу)',
            marker='🍏'
        ),
        as_marked_section(
            Bold('Нельзя:'),
            'Почта',
            'Голуби',
            marker='❌'
        ),
        sep='\n_______________________________________\n'
    )
    await message.answer(text.as_html())

# # магические фильтры: .photo, .audio и тд, фильтры можно комбинировать ',' - и, '|' - или, '&' - и
# @user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'варианты'))
# async def shipping_cmd(message: types.Message):
#     await message.answer('Это магический фильтр!')

# инвертирует выражение, отлавливать всё что не подходит под фильтр
# @user_private_router.message(~(F.text.lower().contains('варианты доставки')))

# магические фильтры: .photo, .audio и тд
@user_private_router.message(F.text.lower().contains('варианты доставки'))
async def shipping_cmd(message: types.Message):
    await message.answer('<s>Это магический фильтр2!</s>')

# представление для отображения клавиатуры контактов
@user_private_router.message(F.text.lower().contains('контакты'))
async def get_menu_contacts(message: types.Message):
    await message.answer('Меню контактов 🎛', reply_markup=test_kb)

@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f'Номер получен')
    await message.answer(str(message.contact))
    cons(message.contact)

@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f'Локация получена')
    await message.answer(str(message.location))
    cons(message.location)

# # отслеживание события отправки сообщения, если хэндлер в другом файле в него можно прокинуть бота, через bot. - можно
# # посмотреть все доступные методы, bot - используется если в прокте несколько ботов
# @user_private_router.message()
# async def echo(message: types.Message):
#     text = message.text
#
#     # if text in ['Привет', 'привет', 'hi', 'hello']:
#     #     await message.answer('И тебе привет!')
#     # elif text in ['Пока', 'покеда', 'пока', 'досвидания']:
#     #     await message.answer('И тебе пока!')
#     # else:
#     #     await message.answer(f'{message.chat.username} сам такой - "{message.text}"!')
#
#     # await bot.send_message(message.from_user.id, 'Ответ')
#     await  message.answer(message.text)
#     # ответить с упоминанием автора (цитата)
#     await  message.reply(message.text)
#