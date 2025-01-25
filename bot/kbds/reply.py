from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from gpt4.utils import cons


############   CallbackQuery — это данные, которые отправляются боту, когда пользователь нажимает на кнопку с
# ##########   callback_data в инлайн-клавиатуре.


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
    ):

    '''
    Parameters request_contact and request_location must be as indexes of btns args for for buttons you need
    Example:
    get_keyboard(
        'Меню',
        'О магазине',
        'Варианты оплаты',
        'Варианты доставки',
        'Отправить номер телефона',
        placeholder='Что вас интересует',

        этот индекс указывает на индекс 5-ой кнопки 'отправить номер телефона', для contact/location дополнительно
        указываем индексы для того чтобы к кнопке можно было указать булево значение при обьявлении
        request_contact=4,
        size=(2, 2, 1)
    )
    '''

    keyboard = ReplyKeyboardBuilder()
    # cons('keyboard')
    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )

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
