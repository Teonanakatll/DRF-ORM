from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.filters.chat_types import ChatTypeFilter, IsAdmin
from bot.kbds.reply import get_keyboard
from gpt4.utils import cons

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Изменить товар",
    "Удалить товар",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2, 1, 1),
)

@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    # cons(message.text)
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)

@admin_router.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_product(message: types.Message):
    await message.answer("ОК, вот список товаров")

@admin_router.message(F.text == "Изменить товар")
async def change_product(message: types.Message):
    await message.answer("ОК, вот список товаров")

@admin_router.message(F.text == "Удалить товар")
async def delete_product(message: types.Message):
    await message.answer("Выберите товар(ы) для удаления")

#Код ниже для машины состояний (FSM)

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    # словарь для отправки состояний пользователю при возврате на предыдущий шаг
    texts = {
        'AddProduct:name': 'Введите название заново:',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите стоимость заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
    }

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

# указываем какое состояние отлавливает этот хэндлер
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    # обновляем данные состояния
    # cons(f'я ввёл {message.text}')
    await  state.update_data(name=message.text)
    # отправляем ответное сообщение
    await message.answer("Введите описание товара")
    # меняем состояние пользователя, на состояние ввода описания
    await state.set_state(AddProduct.description)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели недопустимые данные, введите текст название товара")

# указываем какое состояние отлавливает этот хэндлер
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    # обновляем данные состояния
    await state.update_data(desription=message.text)
    # отправляем ответное сообщение
    await message.answer("Введите стоимость товара")
    # меняем состояние пользователя на состояние ожидания ввода товара
    await state.set_state(AddProduct.price)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.description)
async def add_description(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недопустимые данные, введите текст описания')

@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.price)
async def add_price(message: types.Message, state: FSMContext):
    await message.answer('Вы ввели недопустимые данные, введите текстом цену')

@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    # возвращаем нашу клавиатуру
    await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))

    # clear() - под капотом использует set_state(state=None), и удаляет данные set_data({})
    await state.clear()

# если пользователь ввёл НЕКОРРЕКТНЫЕ ДАННЫЕ
@admin_router.message(AddProduct.image)
async def add_image(message: types.Message, state: FSMContext):
    await message.answer('Вы отправили недопустимые данные, загрузите фото')