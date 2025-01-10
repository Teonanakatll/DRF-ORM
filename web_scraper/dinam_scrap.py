import requests

from utils import cons

# копируем из заголовков
url = 'https://scrapingclub.com/exercise/ajaxdetail/'

# fetch/xhr иньекции возвращают данные ЧЕРЕЗ ДРУГОЙ УРЛ ищем в заголовках, тип fetch/xhr,
#   content-type: 'application/json'/, в предварительном просмотре находится сам словарь
response = requests.get(url).json()

from requests import Session
from bs4 import BeautifulSoup
import time
import random

# сайт может проверить один ли и тотже пользователь запрашивает подгружаемые страницы
# всё как и в верху, только content-type: 'text/html'
base_url = 'https://scrapingclub.com/exercise/list_infinite_scroll/'

headers = {"user-agent": "Mozila/5.0 (Scrap Your Site)"}

def main(base_url):
    s = Session()
    s.headers.update(headers)

    count = 1
    pagination = 0
    while True:
        if count > 1:
            url = base_url + '?page=' + str(count)
        else:
            url = base_url

        response = s.get(url)
        # # записываем ответ сервера в html файл при первой загрузке
        # with open('data.html', 'w', encoding='utf-8') as r:
        #     r.write(response.text)
        soup = BeautifulSoup(response.text, 'lxml')

        if count == 1:
            pagination = int(soup.find('nav', class_='pagination').find_all('span', class_='page')[-2].text)

        cards = soup.find_all('div', class_='w-full rounded border post')

        num = 0
        lst = []
        for card in cards:
            num += 1
            name = card.select('h4 a')[0].text
            # можно напрямую из родительского тега вытащить но будут переносы строк...
            # name = card.find('h4').text
            price = card.find('h5').text
            lst.append([price, name])
            cons(name, price)
        cons(count)
        time.sleep(random.choice([1, 2, 3]))
        if count == pagination:
            break
        count += 1
        # cons(lst)

# main(base_url)

def count_pages(num):
    twenty = 20
    if num < 11:
        num += 1
        cons(num)
        return num
    elif num == 11:
        num = twenty
        cons(num)
        return num
    elif num >= 20:
        num += 10
        cons(num)
        return num

def download(url):
    resp = requests.get(url, stream=True)
    r = open('C:\\Users\\Славик\\Desktop\\pikabu\\' + url.split('/')[-1], 'wb')
    for i in resp.iter_content(1024*1024):
        r.write(i)
        r.close()


                                                   # СКРАПИНГ ДИНАМИЧЕСКОГО САЙТА

# url = 'https://pikabu.ru/tag/%D0%9C%D0%B5%D0%BC%D1%8B/hot/tag/%D0%9C%D0%B5%D0%BC%D1%8B/hot?page=9'
base_url = 'https://pikabu.ru/tag/%D0%9C%D0%B5%D0%BC%D1%8B/hot'

headers = {"user-agent": "Mozila/5.0 (Scrap Your Site)"}

def get_site():
    s = Session()
    s.headers.update(headers)

    count = 1
    pag_num = 1
    while True:
        url = base_url if pag_num == 1 else f'{base_url}?page={pag_num}'
        response = s.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        pagination = int(soup.find_all('a', class_='pagination__page')[-1].text)

        # cons(pages)
        articles = soup.find_all('article', class_='story')
        for i in articles:
            # cons(i.select('h2 a'))
            text, img_link = 'Нет текста', 'Нет фото'
            if i.find('a', class_='story__title-link'):
                text = i.find('a', class_='story__title-link').text
            if i.find('img', class_='story-image__image'):
                img_link = i.find('img', class_='story-image__image').get('data-src')
            if img_link != 'Нет фото' and img_link != None:
                count += 1
                download(img_link)
            cons(count)
            cons(text)
            cons(img_link)

        time.sleep(random.uniform(1, 4))
        pag_num = count_pages(pag_num)
        if pag_num == pagination:
            break

    cons(len(articles))
get_site()
