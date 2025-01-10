import requests
import xlsxwriter
from bs4 import BeautifulSoup
from utils import cons
from time import sleep

url = 'https://mybook.ru/author/karlos-kastaneda/citations/?page='

def get_anekdot():
    c = 1
    count = 0
    # anek_list = []
    while c > 0:
        response = requests.get(f'https://mybook.ru/author/karlos-kastaneda/citations/?page={c}')
        sleep(3)
        soup = BeautifulSoup(response.text, 'lxml')
        quotes = soup.find_all('div', class_='umqv7l-0 cdTNHg')
        if quotes:
            c += 1
            for a in quotes:
                count += 1
                dct = {}
                if a.find('div', class_='text'):
                    dct['анекдот'] = a.find('div', class_='text').text
                    dct['id'] = a.get('data-id')
                    # anek_list.append(dct)
                    cons(count)
                    cons(dct)
                    yield dct['анекдот'], dct['id']
                # else:
                #     cons('Пустой блок')
        else:
            c = 0
            cons(f'Всего: {count} анекдотов')
            # cons(anek_list)


def exel_folder(parametr, folder_name):
    book = xlsxwriter.Workbook(f'C:\\Users\\Славик\\Desktop\\{folder_name}.xlsx')
    page = book.add_worksheet('анекдот')

    row = 0
    column = 0

    page.set_column('A:A', 10)
    page.set_column('B:B', 50)
    for i in parametr():
        page.write(row, column, i[1])
        page.write(row, column+1, i[0])
        row += 1

    book.close()

# exel_folder(get_anekdot, 'o_0)

url2 = 'https://mybook.ru/author/karlos-kastaneda/citations/?page='

def go_scrap_costanedu():
    count = 1
    num_quotes = 0
    while count < 25:
        response = requests.get(f'https://mybook.ru/author/karlos-kastaneda/citations/?page={count}')
        soup = BeautifulSoup(response.text, 'lxml')
        sleep(3)
        blocks = soup.find_all('div', class_='umqv7l-0 cdTNHg')
        if blocks:
            count += 1
            for i in blocks:
                num_quotes += 1
                string = i.find('a').get('href').split('/')[-2]
                text = i.select('article div div div')[0].text
                cons(num_quotes)
                cons(string)
                cons(text)

# go_scrap_costanedu()

url = f'http://batona.net/prikol/'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def download(url):
    response = requests.get(url, stream=True)
    r = open('C:\\Users\\Славик\\Desktop\\o_O_mem\\' + url.split('/')[-1], 'wb')
    for value in response.iter_content(1024*1024):
        r.write(value)
        r.close()


def get_mems():
    page = 1
    num = 0
    while page < 6:
        response = requests.get(f'http://batona.net/prikol/page/{page}/', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        sleep(3)
        blocks = soup.find_all('td', class_='newsText')

        if blocks:
            page +=1
            for i in blocks:
                num += 1
                title = i.find('a').text.split('(')[0].split('№')[0]
                img_link = 'http://batona.net' + i.find('img').get('src')
                download(img_link)
                cons(num)
                cons(img_link)
                cons(title)
        else:
            page = 100
    cons(f'Всего: {num} мемов.')
get_mems()
# cons(len(blocks))

#                                                    # СКРАПИНГ ДИНАМИЧЕСКОГО САЙТА
#
# url = 'https://pikabu.ru/tag/%D0%9C%D0%B5%D0%BC%D1%8B/hot/tag/%D0%9C%D0%B5%D0%BC%D1%8B/hot?page=9'
