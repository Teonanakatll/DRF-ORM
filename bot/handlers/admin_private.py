from html import escape

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.orm_query import orm_add_product, orm_get_products, orm_delete_product, orm_get_product, \
    orm_update_product, orm_get_categories, orm_change_banner_image, orm_get_info_pages
from bot.filters.chat_types import ChatTypeFilter, IsAdmin
from bot.kbds.inline import get_callback_btns
from bot.kbds.reply import get_keyboard
from gpt4.utils import cons

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Добавить/Изменить банер",
    placeholder="Выберите действие",
    # способ размещения кнопок
    # sizes=(2, 1, 1),
    sizes=(2,),
)

# перенесли класс вверх для того чтобы он был доступен для всех хэндлеров и мы могли реализовать не только
# создание но и изменение продукта
class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    # добавляем в машину поле product_for_change для хранения экземпляра продукта и доступа
    # к нему во всех хэндлерах состояний
    product_for_change = None

    # словарь для отправки состояний пользователю при возврате на предыдущий шаг
    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    # cons(message.text)
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Ассортимент")
async def admin_features(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f'category_{category.id}' for category in categories}
    await message.answer('Выберите категорию', reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):

    # вытаскиваем из collback id категории
    category_id = callback.data.split('_')[-1]

    # проходим циклом по товарам полученым из функции orm_query.py/orm_get_products()
    for product in await orm_get_products(session, int(category_id)):
        await  callback.message.answer_photo(
            product.image,
            caption=f'<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}',
            # у answer_photo тоже есть параметр reply_markup - для указания клавиатуры, вызываем нашу финкцию из
            # inline.py и передаём ей данные кнопок каторые мы хотим отрисовать под каждым продуктом
            reply_markup=get_callback_btns(btns={
                'Удалить': f'delete_{product.id}',
                'Изменить': f'change_{product.id}'
            },
                sizes=(2,)
            ),

        )

    await callback.answer("ОК, вот список товаров ⏫")

# хэндлер для отлова и обработки callback_query со строкой 'delete_
@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_porduct_callback(callback: types.CallbackQuery, session: AsyncSession):

    # вырезаем из сообщения id товаро
    product_id = callback.data.split('_')[-1]
    # вызываем нашу кастомную функцию из orm_query.py/orm_delete_product()
    await orm_delete_product(session, int(product_id))

    # этот ответ отправляем серверу чтобы показать что кнопка была нажата, перданный текст покажется
    # посреди экрано во всплывающем уведомлении, show_alert: bool | None = None - если указать этот параметр
    # сообщение будет с кнопкой 'Ok' которую пользователю необходимо будет нажать чтобы сообщение пропало
    await callback.answer('Товар удалён')
    await callback.message.answer('Товар удалён!')  # сообщение в чат


########################## МИКРО FSM ДЛЯ ЗАГРУЗКИ/ИЗМЕНЕНИЯ БАНЕРОВ ####################################

class AddBaner(StatesGroup):
    image = State()

# Отправляем перечень информационных страниц бота и становимся в состояние отправки photo
@admin_router.message(StateFilter(None), F.text == 'Добавить/Изменить банер')
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f'Отправьте фото банера. \n В описании укажите для какой страницы: \n {", ".join(pages_names)}')
    await state.set_state(AddBaner.image)

# Добавляем/изменяем изображение в таблице (там уже есть записанные страницы с именими:
# main, catalog, cart(для пустой корзины), about, payment, shipping.
@admin_router.message(AddBaner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f'Введите нормальное название страницы, например: \n {", ".join(pages_names)}')
        return

    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer('Баннер добавлен/изменён.')
    await state.clear()

# ловим некорректный ввод
@admin_router.message(AddBaner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer('Отправьте фото баннера или отмена.')


# хэндлер который обрабатывает МАШИНУ СОСТОЯНИЙ ДЛЯ callback_query, у пользователя не должно быть никакого состояния
@admin_router.callback_query(StateFilter(None), F.data.startswith('change'))
async def change_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split('_')[-1]

    # вызываем нашу функцию которая возвращает обьект Product
    product_for_change = await orm_get_product(session, int(product_id))

    # в поле product_for_change передаём продукт для того чтобы мы имели
    # доступ к нему в других хэндлерах мошины состояний
    AddProduct.product_for_change = product_for_change
    await callback.answer()
    await callback.message.answer(
        # удаляем клавиатуру с ассортиментом, так как пользователь выбрал изменить товар
        'Введите название товара', reply_markup=types.ReplyKeyboardRemove()
    )

    # становимся в состояние ожидания ввода имени
    await state.set_state(AddProduct.name)



#                           КОД НИЖЕ ДЛЯ МАШИНЫ СОСТОЯНИЙ (FSM)


# StateFilter(None) - проверяем что у пользователя нет октивных состояний
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
# state: FSMContext - для каждого пользователя дополнительно прокидываем параметр context в каждый хэндлер
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Введите название товара", reply_markup=types.ReplyKeyboardRemove())
    # после удаления основной клавиатуры, указываем в какое состояние ожидания мы становимся
    # тоесть в состояние ожидания ввода имени
    await state.set_state(AddProduct.name)
    # для корректного принта state необходимо вызывать через await
    # cons(f'get.state {await state.get_state()}')

# StateFilter('*') - проверяем есть ли у пользователя любое состояние
@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    # cons('отмена')
    current_state = await state.get_state()
    # cons(current_state)
    if current_state is None:
        return

    await state.clear()  # ачищаем состояния полностью
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)

@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    # получаем текущее состояние
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer('Пдедыдущего шаго нет, или введите название товара или напишите - отмена')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            # получаем описание предыдущего шага из добавленного нами словаря texts как параметр SFM (машины состояний)
            # в качетсве ключа передаём состояние предыдущего состояния
            await message.answer(f'Ок, вы вернулись к прошлому шагу \n {AddProduct.texts[previous.state]}')
            return
        previous = step

# указываем какое состояние отлавливает этот хэндлер, or_f() - аналог 'или' или одно условие должно совпасть или другое
# или это должен быть текст или это должно быть сообщение с точкой '.' - что значит оставить старое название
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    # если сообщение точка, тогда берём имя из текущего экзэмпляра Product в переменной product_for_change
    if message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        # сдесь можно сделать какую либо дополнительную проверку и выйти из хэндлера не менмяя состояния
        # с отправкой соответствующего сообщения, например:
        if 4 >= len(message.text) >=140:
            await message.answer('Название товара не должно превышать 140 символов. \n Или быть короче 5 символов. \n Введите заново')
            return

        # обновляем данные состояния
        await  state.update_data(name=message.text)
    # отправляем ответное сообщение
    await message.answer("Введите описание товара")
    # меняем состояние пользователя, на состояние ввода описания
    await state.set_state(AddProduct.description)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные, введите текст название товара")


# указываем какое состояние отлавливает этот хэндлер
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.':
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                'Название товара не должно превышать 140 символов. \n Или быть короче 5 символов. \n Введите заново')
            return

        # обновляем данные состояния
        await state.update_data(description=message.text)

    # берём категории из бд
    categories = await orm_get_categories(session)
    # создаём словарь в котором имя категории ключ а айди категории его значение
    btns = {category.name: str(category.id) for category in categories}
    await message.answer('Выберите категорию', reply_markup=get_callback_btns(btns=btns))

    # меняем состояние пользователя на состояние ожидания выбора категории
    await state.set_state(AddProduct.category)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недопустимые данные, введите текст описания')


# ловим callback выбора категории
@admin_router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer('Теперь введите цену товара.')
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите кнопку категории.')
        await callback.answer()

#Ловим любые некорректные действия, кроме нажатия на кнопку выбора категории
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Выберите кнопоку категории.'")


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == '.' and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        await state.update_data(price=message.text)

    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недопустимые данные, введите текстом цену')


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == '.'))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.' and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer('Отправьте фото пищи.')
        return

    data = await state.get_data()
    await message.answer(str(data))

    try:
        # проверяем изменяется ли товар, тоесть есть ли в нём переменная product_for_change
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)

        # иначе создаём товар
        else:
            # вызываем функцию для создания из orm_query.py
            await orm_add_product(session, data)

            await message.answer('Товар добавлен/изменён', reply_markup=ADMIN_KB)

    except Exception as e:
        error_message = escape(str(e))  # Экранируем текст ошибки
        await message.answer(f'Ошибка: \n{error_message}\nОбратитесь к програмисту, он опять хочет денег', reply_markup=ADMIN_KB,)

    # В ЛЮБОМ СЛУЧАЕ СБРАСЫВАЕМ (finally) состояния и переменную product_for_change
    finally:
        # убираем товар из переменной машины состояний
        AddProduct.product_for_change = None
        # clear() - под капотом использует set_state(state=None), и удаляет данные set_data({})
        await state.clear()

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer('Вы отправили недопустимые данные, загрузите фото')