import asyncio
import aiohttp

from gpt4.utils import cons

TOKEN = '7901888470:AAF8eGnqH-0tUZblawrmVpc5xxlI1WZqKPg'

URL = f'https://api.telegram.org/bot{TOKEN}'

async  def send_message(chat_id, text):
    #  если ты используешь обычные синхронные контекстные менеджеры (без async), создание сессии и отправка запроса
    #  будут блокировать выполнение программы до их завершения.
    #  Контекстный менеджер — это объект, который управляет ресурсами, такими как файлы, соединения или сессии, и
    #  гарантирует их корректное закрытие после использ. В Python они часто использ. с конструкцией with или async with
    async with aiohttp.ClientSession() as session:
        params = {'chat_id': chat_id, 'text': text}
        async  with session.post(URL + 'sendMessage', data=params) as response:
            # после await функция продолжит выполнение если в ней есть дополнительные шаги
            await response.json()

async def handle_updates(update):
    message = update.get('message', False)
    if message:
        chat_id = message['chat']['id']
        text = message.get('text', False)
        if text:
            await send_message(chat_id, f'Эхо: {text}')
        else:
            await send_message(chat_id, 'Я работаю только с текстом')

async def get_updates():
    offset = None
    async with aiohttp.ClientSession() as session:
        while True:
            params = {'timeout': 10, 'offset': offset}
            async with session.post(URL + 'getUpdates', data=params) as response:
                updates = await response.json()
                cons(updates)
                if len(updates['result']) > 0:
                    offset = updates['result'][-1]['update_id'] + 1
                    for update in updates['result']:
                        await handle_updates(update)


                        for_print = update.copy()
                        for_print['message']['from']['id'] = 1234567890
                        for_print['message']['chat']['id'] = 1234567890
                        print(for_print)

async def main():
    await get_updates()

asyncio.run(main())
