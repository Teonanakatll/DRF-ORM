from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
# предок всех событий TelegramObject, вписываем его вместо Message если мидлвеар подключаем через Dispatcher()
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


# служит для пробрасывания сессии в каждый хэндлер, будет доступно как и message
class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            # по ключу session добавляем сам обьект сессии
            data['session'] = session
            return await handler(event, data)

# class CounterMiddleware(BaseMiddleware):
#     def __init__(self) -> None:
#         self.counter = 0
#
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
#         # формируем словарь для прокидывания в хэндлеры
#         self.counter += 1
#         data['counter'] = self.counter
#         return await handler(event, data)