import requests
from utils import cons
from random import randint

req = requests.get("https://jsonplaceholder.typicode.com/posts")
# cons(req.text)
lst_id = []
for i in req.json():
    if i['userId'] not in lst_id:
        lst_id.append(i['userId'])
# cons(lst_id)

lst_user = []
id = 10
for i in req.json():
    if i['userId'] == id:
        lst_user.append(i)
# cons(lst_user)

rang = range(70, 81)
lst_range = []
for i in req.json():
    if i['id'] in rang:
        lst_range.append(i)
# cons(lst_range)
req = req.json()

# for key, values in req[0].items():
#     cons(key, values)
#
# cons(req[0].values())
# cons(req[0].keys())

# for i in req:
#     if 'title' in i.keys():
#         cons('Yes')

for i in req:
    rand = randint(1, 21)
    i['userId'] = rand
    i['hren'] = rand
    cons(i.keys())

