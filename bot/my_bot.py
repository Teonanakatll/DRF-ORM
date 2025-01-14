# Aiogram использует async/await для выполнения асинхронных операций, таких как отправка запросов к Telegram API,
# поэтому asyncio нужен для запуска событийного цикла.
import asyncio
import os

# types - это модуль, который содержит типы данных, используемые в Telegram Bot API.
# types.Message — объект, представляющий сообщение от пользователя.
# types.CallbackQuery — объект, представляющий callback-запрос от inline-кнопки.
from aiogram import Bot, Dispatcher, types
# фильтры сообщений
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import BotCommandScopeAllPrivateChats

from bot.handlers.admin_private import admin_router
from bot.handlers.user_private import user_private_router
from bot.handlers.user_group import user_group_router
from bot.common.bot_cmds_list import private
from gpt4.utils import cons

from dotenv import find_dotenv, load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv(find_dotenv())
# storage = MemoryStorage()

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# переменная для хранения админов
bot.my_admins_list = []

# cons('from my_bot.py my_admins_list', bot.my_admins_list)

# список разрешённых обновлений которые необходимо получать и обрабатывать в боте
ALLOWED_UPDATES = ['message, edited_message']

# Dispatcher это менеджер, который управляет обработкой входящих обновлений (сообщений, команд, callback-данных).
# Он помогает "назначать" функции для обработки конкретных типов сообщений или команд.
# По умолчанию использует MemoryStorage - тоесть хранит данные в оперативной памяти
dp = Dispatcher()

# include_router/s - можно пердавать в диспетчер роутеры по одному или списком
dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


# прослушивание сообщений для нашего бота, этот процесс повторяется бесконечно, пока бот работает.
# start_polling() — это метод, который позволяет боту самому запрашивать обновления у Telegram сервера (путём
# периодического отправления запросов). Такой подход обычно используется на этапе разработки или в проектах, где нет
# необходимости использовать вебхуки. Просто настроить. Не нужен домен, SSL-сертификат или сложная инфраструктура.
# Хорошо подходит для разработки и тестирования.
#
# set_webhook() — это метод, который настраивает Telegram на отправку обновлений на ваш сервер. Вместо того чтобы бот
# "опрашивал" Telegram, он ждёт, пока Telegram сам отправит обновления на указанный веб-адрес. Telegram отправляет
# POST-запрос на указанный тобой адрес, когда появляется новое сообщение. Тебе нужен сервер, который будет слушать
# запросы и обрабатывать их. должен быть домен (например, https://yourbotdomain.com) с поддержкой HTTPS. Более эфф.
# способ обработки обновлений (меньше трафика и задержек). Telegram отправляет данные только при наличии новых событий.
async def main():
    cons('TRue')
    await bot.delete_webhook(drop_pending_updates=True)  # игнорирует сообщения отправленные когда бот был оффлайн

    # для удаления команд
    # await bot.set_my_commands(scope=types.BotCommandScopeAllPrivateChats())

    # указываем для каких чатов создаём меню команд
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
