import requests
from bs4 import BeautifulSoup
from apikey import API_TOKEN

from utils import cons

params = {
    "q": "Rostov-na-Donu",
    # "q": "Tbilisi",
    # "q": "Tokio",
    # "limit": 5,
    "appid": API_TOKEN,
    "units": "metric"
}

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)

# response = requests.get("https://httpbin.org/headers", headers=headers)


#                                    post Запрос

data = {
    "custname": "Borya",
    "custtel": 8988345234,
    "custemail": "Sobaka@sobaka.gav",
    "size": "medium",
    "topping": "bacon",
    "delivery": "13:45",
    "comments": "bystro"
}

# response = requests.post("https://httpbin.org/post", headers=headers, data=data)


variable = requests.Session()
#
# data = ''
# aaa = variable.get("https://httpbin.org/post", headers=headers)  # вытаскиваем куки и добавляем в словарь
response2 = variable.post("https://httpbin.org/post", headers=headers, data=data, allow_redirects=True)


# cons(response.status_code)
# cons(response.headers)
# cons(response.content)  # байтовая строка
# cons(response)   # <Response [200]>
# x = response.json()
x = response2
cons(x.text)

# cons(x['weather'][0]['main'])
# cons(x['main']['temp'])   # представляет джсон словарь

# смотрим какие заголовки возвращает сайт, какой Content-Type
#response.heders