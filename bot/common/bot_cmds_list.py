from aiogram.types import BotCommand

# кнобка меню внизу слева
private = [
    BotCommand(command='menu', description='Посмотреть меню'),
    BotCommand(command='about', description='О магазине'),
    BotCommand(command='payment', description='Варианты оплаты'),
    BotCommand(command='shipping', description='Варианты доставки'),
]
