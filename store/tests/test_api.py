import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg, F
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from gpt4.utils import cons
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer
from django.test.utils import CaptureQueriesContext

from rich.console import Console
console = Console()


class BooksApiTestCase(APITestCase):
    # сериализация это преобразование обьектов пайтон в json, а десериализация наоборот из json в обьект пайтон
    # в тесте апи почти не тестируются поля, тестируются статус-коды и данные ответа (их структура и значения)
    def setUp(self):
        self.user = User.objects.create(username='test_username')

        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 3', owner=self.user)
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55, author_name='Author 2')

        self.relation = UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get_list(self):
        # создаём url по имени пути
        url = reverse('book-list')

        # чтобы проверить сколько запросов происходит во время запроса, запустим response в контексте
        # CaptureQueriesContext — инструмент Django для мониторинга SQL-запросов, а connection — это
        # объект подключения к базе данных, будет логировать все SQL-зарпоссы во время его работы
        with CaptureQueriesContext(connection) as queries:
            # client это тестовый клиент для имитации http запросов к приложению в тестах, get - get запрос
            response = self.client.get(url)
            self.assertEqual(2, len(queries))

        books = Book.objects.annotate(annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                      # rating=Avg('userbookrelation__rate'),
                                      owner_name=F('owner__username')) \
                                      .select_related('owner').prefetch_related('readers').order_by('id')


        # создаём сериализатор и передаём в него созданные обьекты
        serializer_data = BooksSerializer(books, many=True).data

        # проверяем статус ответа
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # сравниваем данные созданные сериализатором напрямую и полученные слиентом в ответе
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        # self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_detail(self):
        url = reverse('book-detail', args=(self.book_3.id,))
        response = self.client.get(url)

        book = Book.objects.filter(id=self.book_3.id).annotate(
                                                annotated_likes=Count(Case(When(userbookrelation__like=True), then=1)),
                                                owner_name=F('owner__username'))[0]

        serializer_data = BooksSerializer(book).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55})

        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
                                                annotated_likes=Count(Case(When(userbookrelation__like=True), then=1)),
                                                owner_name=F('owner__username')
                                                ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})

        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
                                                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                                owner_name=F('owner__username')
                                                ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(serializer_data, response.data)



    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-author_name'})

        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id, self.book_1.id]).annotate(
                                                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                                owner_name=F('owner__username'))

        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name': 'Programming in Python 3',
            'price': 1500,
            'author_name': 'Mark Summerfield'
        }
        json_data = json.dumps(data)
        # логинимся через клиент
        self.client.force_login(self.user)

        response = self.client.post(url, data=json_data, content_type='application/json')
        # print('All books', Book.objects.all()[0].id)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        # логинимся через клиент
        self.client.force_login(self.user)

        response = self.client.put(url, data=json_data, content_type='application/json')
        # обновляем обьект из базы данных
        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        # логинимся через клиент
        self.client.force_login(self.user2)

        response = self.client.put(url, data=json_data, content_type='application/json')
        # обновляем обьект из базы данных
        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
        #                                         code='permission_denied')}, response.data)
        # чтобы не зависить от текста ошибки ставим проверку на её код
        # cons(response.data['detail'])
        self.assertEqual('You do not have permission to perform this action.', response.data['detail'])
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='staff', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        # логинимся через клиент
        self.client.force_login(self.user2)

        response = self.client.put(url, data=json_data, content_type='application/json')
        # обновляем обьект из базы данных
        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # print(Book.objects.all().values())
        self.assertEqual(575, self.book_1.price)

    def test_partial_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': 'The Fountain',
        }
        json_data = json.dumps(data)
        # логинимся через клиент
        self.client.force_login(self.user)

        response = self.client.patch(url, data=json_data, content_type='application/json')
        # обновляем обьект из базы данных
        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('The Fountain', self.book_1.name)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_2.id,))

        # логинимся через клиент
        self.client.force_login(self.user)
        response = self.client.delete(url)
        delete_book = Book.objects.filter(id=self.book_2.id).exists()

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(False, delete_book)
        self.assertEqual(2, Book.objects.all().count())

    def test_delete_not_owner(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_3.id,))

        # логинимся через клиент
        self.client.force_login(self.user)
        response = self.client.delete(url)
        delete_book = Book.objects.filter(id=self.book_3.id).exists()

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(True, delete_book)


class BooksRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')

        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 3', owner=self.user)

    def test_like(self):
        # создаём url по имени пути
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'like': True
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        # client это тестовый клиент для имитации http запросов к приложению в тестах, get - get запрос
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            'in_bookmarks': True
        }

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        data = {
            'rate': 5
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(5, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        data = {
            'rate': 6
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        # в проверку условия можно добавить ещё один 3-й параметр который будет выведен если тест упал
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        # cons(response.data['rate'][0].code)
        # cons(response.data)
# обращ. к словарю ответа data, по ключу 'rate' и инд. [0] (тест. поле) получаем обьект ошибки, обращаясь к атриб. .code
# который сдержит фиксированый код ошибки берём значение, .string - текст ошибки (зависит от передаваемых данных)
        self.assertEqual('invalid_choice', response.data['rate'][0].code)
        r = UserBookRelation.objects.get(user=self.user, book=self.book_1)
        self.assertFalse(r.rate)


    def test_comment(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'comment': 'Первый йопте!'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(book=self.book_1, user=self.user)
        self.assertEqual('Первый йопте!', relation.comment)
