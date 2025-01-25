import math

from aiogram import types
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.database.models import Product, Banner, Category, User, Cart
from gpt4.utils import cons


class Paginator:
    ''' !!!!!!!!!!!!!!!!!   ПО УМОЛЧАНИ УСТАНАВЛИВАЕТ НАЧАЛЬНОЕ ЗНАЧЕНИЕ page/per_page 1 ЧТО ПОЗВОЛЯЕТ ВЫПОЛНЯТЬ
    ДАЛЬНЕЙШИЕ ВЫЧИСЛЕНИЯ В ДР ФУНКЦИЯХ '''
    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        # math.ceil - округление в большую сторону до целого числа
        self.pages = math.ceil(self.len / self.per_page)

    # расчёт среза и срез страницы
    def __get_slice(self):
        # чтобы вывести срез записей текущей страницы отнимаем 1 от текущей страницы и умножаем на количество записей
        # на странице, например текущая страница 1: 1-1=0 * 5, тоесть отсчёт будет от нулевой записи
        start = (self.page - 1) * self.per_page
        # окончанием среза будет количеством записей на странице 0+5
        stop = start + self.per_page
        return self.array[start:stop]

    # возврат среза
    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    # проверка следующей страницы
    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    # проверка предыдущей страницы
    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    # запрос следующей страницы
    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError('Next page does not exist. Use has_next() to check before.')

    # запрос предыдущей страницы
    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.get_page()
        raise IndexError('Previous page does not exist. Use has_previous() to check before.')


############################ Работа с банерами (информационными страницами) ######################

# банеры добавляются при создании базы в файле my_bot по данным полученным из common/texts_for_db
async def orm_add_baner_description(session: AsyncSession, data: dict):
    # добавляем навый или изменяем сществующий по именам пунктов меню: main, about, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    # если баннеры уже есть выходим
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()])
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    rsult = await session.execute(query)
    return rsult.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


################################### Категории ######################################

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


# категории добавляются при создании базы в файле my_bot по данным полученным из common/texts_for_db
async def orm_creat_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    # если категории уже есть выходим
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


##################### Админка: добавить/изменить/удалить товар #########################

# функция добавления товара
async def orm_add_product(session: AsyncSession, data):
    # создаём обьект класса модели которую мы создали в models.py
    obj = Product(
        # и в поля модели передаём данные полученные из мошины состояний
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        image=data['image'],
        category_id=int(data['category'])
    )
    # в сессию из midlware передаём наш обьект модели
    session.add(obj)
    # сохраняем изменения в бд
    await session.commit()

# функция выдаёт список всех товаров
async def orm_get_products(session: AsyncSession, category_id: int):   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # проверяем флаг 000 для загрузки всех существующих товаров
    # флаг сделад ТОЛЬКО ДЛЯ ТОГО ЧТОБЫ НЕ УДАЛЯТЬ ХЭНДЛЕРЫ user_private.py
    # if catetory_id == 000:
    #     query = select(Product)
    #     result = await session.execute(query)
    #     await message.answer('HOHOHOHOHOHOHOHOHOHOHOH')
    #     return result.scalars().all()
    # else:
    # помогает сформировать запрос выборки данных из бд (все колонки всех записей)
    query = select(Product).where(Product.category_id == category_id)
    result = await session.execute(query)  # выполняем запрос
    # Метод scalars() извлекает только значения из выбранных столбцов, игнорируя дополнительную информацию, которая
    # могла быть возвращена запросом. all(): собирает эти значения в список
    return result.scalars().all()

async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    # scalar() — если тебе нужно одно значение. Пример: Количество записей, конкретный идентификатор.
    return result.scalar()

async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        image=data['image'],
        category_id=int(data['category'])),

    await session.execute(query)
    await session.commit()

async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


################################ Добавляем юзера в бд ##########################

async def orm_add_user(
        session: AsyncSession,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        phone: str | None = None,
):
    # проверяем есть ли пользователь, если нет то добавляем
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone))
        await session.commit()


############################# Работа с корзинами ###############################3

async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    # избавляемся от n+1 - joinedload(Cart.product)
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()


async def orm_get_user_carts(session: AsyncSession, user_id: int):
    query = select(Cart).where(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    cons('orm_delete_from_cart()', user_id, product_id)
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False
