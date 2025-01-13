from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kb = ReplyKeyboardMarkup(
    # описание клавиатуры
    keyboard=[
        [
          KeyboardButton(text='Меню'),
          KeyboardButton(text='О магазине'),
        ],
        [
            KeyboardButton(text='Варианты доставки'),
            KeyboardButton(text='Варианты оплаты'),
        ]
    ],
    resize_keyboard=True,
    # подсказка отображаемая в строке сообщений
    input_field_placeholder='Что вас интересует?'
)

# удаление клавиатуры
del_kbd = ReplyKeyboardRemove()


start_kb2 = ReplyKeyboardBuilder()
start_kb2.add(
    KeyboardButton(text='Меню'),
    KeyboardButton(text='О магазине'),
    KeyboardButton(text='Варианты доставки'),
    KeyboardButton(text='Варианты оплаты'),
)
# устанавливаем количество рядов и кнопок
start_kb2.adjust(2, 2)

start_kb3 = ReplyKeyboardBuilder()
start_kb3.attach(start_kb2)                              # attach() - расширяем переданную клавиатуру
start_kb3.row(KeyboardButton(text='Оставить отзыв'))     # row() - добавляем кнопку новым рядом
# подключаем нопку на нижнюю клавиатуру, которая
start_kb3.row()

test_kb = ReplyKeyboardMarkup(
    keyboard=[
    [
        KeyboardButton(text='Создать опрос', request_poll=KeyboardButtonPollType()),
    ],
    [
        KeyboardButton(text='Отправить номер 📱', request_contact=True),
        KeyboardButton(text='Отправить локацию ⬇ 💎', request_location=True),
    ],

], resize_keyboard=True, input_field_placeholder='Меню контактов')
