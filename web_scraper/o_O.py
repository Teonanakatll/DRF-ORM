from random import randint

import requests
from bs4 import BeautifulSoup
from time import sleep
from utils import cons

# pip install beautifulsoup4 requests lxml XlsxWriter

url = f'https://scrapingclub.com/exercise/list_basic/?page=1'

response = requests.get(url)

# lxml в сочетании с BeautifulSoup она служит как более быстрый и мощный парсер, заменяя стандартный html.parser. Он
# оптимизирован для обработки больших объемов данных и поддерживает XPath для более сложных запросов.
soup = BeautifulSoup(response.text, 'lxml')   # html.parser стандартный парсер, не требует установки (медленный)

# find по умолчанию возвращает первый указанный тег
data = soup.find('div', class_="w-full rounded border")
data2 = soup.find_all('div', class_="w-full rounded border")  # возвращает все подходящие теги

name = data.find("h4").find("a").text.replace("\n", "")
price = data.find("h5").text
# через get() получаем значения атрибутов, добавляем адрес сайта тк вытягиваем мы отностельную ссылку
link_img = "https://scrapingclub.com" + data.find("img", class_="card-img-top img-fluid").get("src")

# cons(data)
# cons(name + "\n" + price + "\n" + link_img + "\n\n")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# примеры использования парсера обьектов находящихся на страницах пагинации, и с заходом в отдельные айтемы
def parse_with_list():
    list_card_url = []

    for count in range(1, 8):
        sleep(3)  # уменьшаем нагрузку на сайт
        url = f'https://scrapingclub.com/exercise/list_basic/?page={count}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find_all("div", class_="w-full rounded border")
        for i in data:
            # когда необходима спарсить данные которые просто находятся на странице
            # name = i.find("h4").find("a").text.replace("\n", "")
            # price = i.find("h5").text
            # # через get() получаем значения атрибутов, добавляем адрес сайта тк вытягиваем мы отностельную ссылку
            # link_img = "https://scrapingclub.com" + i.find("img", class_="card-img-top img-fluid").get("src")
            # cons(name + "\n" + price + "\n" + link_img + "\n\n")

            # теперь в каждой карточке заходим в описание
            card_url = "https://scrapingclub.com" + i.find("a").get("href")
            list_card_url.append(card_url)
    # cons(list_card_url)
    n = 0
    for i in list_card_url:
        response = requests.get(i, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        link_img = "https://scrapingclub.com" + soup.find("img", class_="card-img-top").get("src")
        name = soup.find("h3", class_="card-title").text
        price = soup.find("h4", class_="card-price").text
        description = soup.find("p", class_="card-description").text
        n += 1
        cons(n)
        cons(name + "\n" + price + "\n" + link_img + "\n" + description + "\n\n")

def download(url, num):
    resp = requests.get(url, stream=True)
    # записываем в байтах, в качестве названия используем url который разрезаем по обратным слешам и берём последний
    r = open('C:\\Users\\Славик\\Desktop\\o_O\\' + str(num) + url.split('/')[-1], 'wb')
    for value in resp.iter_content(1024*1024):
        r.write(value)
    r.close()

def parse_yield():
    for count in range(1, 8):
        url1 = f'https://scrapingclub.com/exercise/list_basic/?page={count}'
        response1 = requests.get(url1, headers=headers)
        soup1 = BeautifulSoup(response1.text, 'lxml')
        data1 = soup1.find_all('div', class_='w-full rounded border')
        for i in data1:
            card_link = 'https://scrapingclub.com' + i.find('a').get('href')
            yield card_link

def array():
    n = 0
    for card_link in parse_yield():
        response1 = requests.get(card_link, headers=headers)
        # sleep(1)
        soup1 = BeautifulSoup(response1.text, 'lxml')

        link_img = 'https://scrapingclub.com' + soup1.find('img', class_='card-img-top').get('src')
        title = soup1.find('h3', class_='card-title').text
        price = soup1.find('h4', class_='card-price').text
        description = soup1.find('p', class_='card-description').text

        n += 1
        download(link_img, n)
        cons(n)
        yield title, price, link_img, description


# parse_yield()