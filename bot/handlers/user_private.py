from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
)

from bot.filters.chat_types import ChatTypeFilter
from bot.handlers.menu_rocessing import get_menu_content
from bot.kbds.inline import get_callback_btns, MenuCallBack

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


# обрабатываем только команду /start всё остальное обрабатывается через callback клавиатуры
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    # get_menu_content() - находится в menu_processing, будет отправлять изображение и клавиатуру
    media, replay_markup = await get_menu_content(session, level=0, menu_name='main')

    await message.answer_photo(media.media, caption=media.caption, reply_markup=replay_markup)


# функция добавляет пользователя в бд и создаёт обьект корзины привязаннфй к этому пользователю
async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    # show_alert=True - чтобы убрать сообщение нужно будет нажать Ок
    await callback.answer('Товар добавлен в корзину.', show_alert=True)


# вызываем метод filter() у нашего кастомного класса фабрики колбэков чтобы отлавливать все сообщения с
# префиксом меню который мы выбрали при инициализации класса
# но чтобы получить в нужном формате данные которые передаюся через фабрику колбэков и с помощю неё формируются,
# нам необходимо указать callback_data: MenuCallBack
@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):

    # если событие отправленно кнопкой 'Купить', меню остаётся темже просто добавляем товар в корзину
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return

    # вызываем функцию async def get_menu_content() - чтобы сформировать клавиатуру в
    # зависимости от переданного level и запроса изображения баннера в зависимости от переданного menu_name
    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        # id аккаутна телеграмм берём просто из callback
        user_id=callback.from_user.id,
    )

    # ток как тут мы уже редактируем сообщение то нам не нужно разбирать его на .medua/.caption,
    # передаём просто экземрляр InputMediaPhoto()
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


####################   ПРИМЕР ПЕРЕДАЧИ ПОЗИЦИОННЫХ АРГУМЕНТОВ
def CommandStarrrrt():
    pass

# @user_private_router.message(CommandStarrrrt())
async def start_cmd(message: types.Message):
    await message.answer("Привет, я виртуальный помощник",
                         # создаём кнопку при нажатии на которую отправляется callback_query сообщение каторое будет
                         # отлавливаться другим хэндлером
                         reply_markup=get_callback_btns(btns={
                             'Нажми меня': 'some_1'
                         }))


@user_private_router.callback_query(F.data.startswith('some_'))
async def counter(callback: types.CallbackQuery):
    number = int(callback.data.split('_')[-1])

    # callback.message.edit_text() - ДЛЯ ТОГО ЧТОБЫ НЕ ОТПРАВЛЯТЬ НОВОЕ СООБЩЕНИЕ ОТВЕТА А РЕДАКТИРОВАТЬ СТАРОЕ
    # автоматически в callback_query и в сообщение подставляеются данные счётчика который увеличивается на 1
    # также у сообщения можно редактировать: edit_caption, edit_date, edit_live_location, edit_media, edit_reply_markup
    await callback.message.edit_text(
        text=f"Нажатий - {number}",
        # создаём кнопку
        reply_markup=get_callback_btns(btns={
            'Нажми еще раз': f'some_{number + 1}'
        }))

# Пример для видео как делать не нужно:
# menu_level_menuName_category_page_productID
# НУЖО ИСПОЛЬЗОВАТЬ ФАБРМКУ КОЛБЭКОВ