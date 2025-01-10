from requests import Session
from bs4 import BeautifulSoup
from time import sleep
from utils import cons

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

work = Session()

work.get('https://quotes.toscrape.com/', headers=headers)

response = work.get('https://quotes.toscrape.com/login', headers=headers)

soup = BeautifulSoup(response.text, 'lxml')

token = soup.find('form').find('input').get('value')
data = {
    'csrf_token': token,
    'username': 'Fox',
    'password': '12345'
}
work.post('https://quotes.toscrape.com/login', headers=headers, data=data, allow_redirects=True)

f = 1
count = 0
quot_list = []
while f:
    response = work.get(f'https://quotes.toscrape.com/page/{f}', headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    quots = soup.find_all('div', class_='quote')
    if quots:
        f += 1
        for i in quots:
            count += 1
            quot = {}
            quot['text'] = i.find('span', class_='text').text
            quot['author'] = i.find('small', class_='author').text
            quot['link'] = i.find_all('a')[1].text
            quot['tag_list'] = []
            tags = i.find_all('a', class_='tag')
            if tags:
                for t in tags:
                    quot['tag_list'].append(t.text)
            quot_list.append(quot)
            cons(count)
            cons(len(quot_list))
            cons(quot)
    else:
        cons(f'Всего: {f} страниц.')
        f = 0

