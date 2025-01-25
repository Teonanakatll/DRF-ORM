from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

############   CallbackQuery — это данные, которые отправляются боту, когда пользователь нажимает на кнопку с
############   callback_data в инлайн-клавиатуре.

# используем класс фильтров для формирования фабрики колбэков, который будет отлавливать сообщения по префиксу
# и указывает типы данных передаваемых параметров (если их передавать в сообщении через _ то ни будут строкой)
from gpt4.utils import cons


class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str
    # параметр может иметь значения int/None и None по умолчанию
    category: int | None = None
    page: int = 1
    product_id: int | None = None


# функция возвращает клавиатуру первого уровня
def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        # в зависимости от назначения кнопки в callback_data записываем level меню на которое она ведёт
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                    # формируем данные для фабрики колбэков
# Сериализует объект в строку: Метод pack() преобразует все данные из объекта MenuCallBack в строку формата
# key1:value1|key2:value2. Это необходимо, потому что callback_data в Telegram принимает только строку
# (размером до 64 байт), а не объект.
                    callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            # если мы используем не add() а Button то в pack() нет необходимости там всё происходит автоматически
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            # при клике на остальные пункты меню мы остаёмся на томже 0 уровне меню
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
            callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
            callback_data=MenuCallBack(level=3, menu_name='cart').pack()))

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(
        *,
        level: int,
        category: int,
        page: int,
        pagination_btns: dict,  # кнопки назад/вперёд, в зависимости от порядка может быть одна или другая
        product_id: int,        # нужен для того чтобы разместить на кнопке купить
        sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
            callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
            callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    # небудет менять клавиатуру, будет выводить сообщение что товар добавлен в корзину, add_to_cart - триггер
    # по катораму мы будем отлавливать это событие
    keyboard.add(InlineKeyboardButton(text='Купить 💵',
            callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == 'next':
            row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            category=category,
                            page=page + 1).pack()))

        elif menu_name == 'previous':
            row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(
                            level=level,
                            menu_name=menu_name,
                            category=category,
                            page=page - 1).pack()))

    return keyboard.row(*row).as_markup()




def get_callback_btns(
    # * - запрет на передачу ненумерованных пораметров
    *,
    # словари btns будут содержать КЛЮЧОМ словаря - название кнопки, ЗНАЧЕНИЕМ словаря - id записи Product которое будет
    # передаваться на сервер при нажатии на кнопку и записываться в параметр callback_data
    btns: dict[str, str],
    sizes: type[int] = (2,)):

    keyboard = InlineKeyboardBuilder()
    # в цикле проходим по списку переданных кнопок и присваиваем text-названию кнопки, а data-параметру callback_data
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_user_cart(
        *,
        level: int,
        page: int | None,
        pagination_btns: dict | None,
        product_id: int | None,
        sizes: type[int] = (3,)
):
    keyboard = InlineKeyboardBuilder()
    # проверяем что корзина не пустая, то формируем клавиатуру полностью
    if page:
        cons('get_user_cart()', product_id)
        keyboard.add(InlineKeyboardButton(text='Удалить',
                  callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1',
                  callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1',
                  callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))

        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == 'next':
                row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == 'previous':
                row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()))

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='На главную 🏠',
                        callback_data=MenuCallBack(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='Заказать',
                        callback_data=MenuCallBack(level=0, menu_name='order').pack()),
        ]
        return keyboard.row(*row2).as_markup()

    # если корзина пустая то отправляем кнопку - На главную
    else:
        keyboard.add(InlineKeyboardButton(text='На главную 🏠',
                    callback_data=MenuCallBack(level=0, menu_name='main').pack()))

        return keyboard.adjust(*sizes).as_markup()


######################## просто примеры

# клвиатура для формирования кнопок с сылками
def get_url_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()

# комбинированная клавиатура для вывода кнопок отправляющих id и кнопок с ссылками
def get_url_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()
