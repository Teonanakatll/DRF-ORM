import json

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.test.utils import CaptureQueriesContext
from slugify import slugify

from gpt4.models import Author, BookG
from gpt4.serializers import AuthorSerializer
from gpt4.utils import cons


class AuthorSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Kroks')

        self.author_1 = Author.objects.create(name='Дон Кихот', birthday='1835-12-25', biography='Don Kihot Biography')
        self.author_2 = Author.objects.create(name='Пушкин', birthday='1875-05-15', biography='Pushkin Biography')

        self.book_1 = BookG.objects.create(title='Еверест', content='Content Book_1', pages=200, author=self.author_1)
        self.book_2 = BookG.objects.create(title='Ельбрус', content='Content Book_2', pages=300, author=self.author_1)
        self.book_3 = BookG.objects.create(title='Казбек', content='Content Book_3', pages=400, author=self.author_2)

        self.base_url = 'http://testserver'

    # получение списка авторов
    def test_get_list(self):
        url = reverse('author-list')
        self.client.force_login(self.user_1)

        # чтобы проверить сколько запросов происходит во время запроса, запустим response в контексте
        # CaptureQueriesContext — инструмент Django для мониторинга SQL-запросов, а connection — это
        # объект подключения к базе данных, будет логировать все SQL-зарпоссы во время его работы
        with CaptureQueriesContext(connection) as queries:
            # client это тестовый клиент для имитации http запросов к приложению в тестах, get - get запрос
            response = self.client.get(url)
            self.assertEqual(4, len(queries))

        context = {'request': response.wsgi_request}
        serializer_data = AuthorSerializer([self.author_1, self.author_2], context=context, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение одного автора
    def test_get_detail(self):
        url = reverse('author-detail', args=(self.author_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        context = {'request': response.wsgi_request}
        serializer_data = AuthorSerializer(self.author_1, context=context).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение несуществующей записи
    def test_get_detail_not_exist(self):
        url = reverse('author-detail', args=(100,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # создание жанра, админом
    def test_post(self):
        self.assertEqual(2, Author.objects.count())
        url = reverse('author-list')
        self.client.force_login(self.user_1)
        data = {
            "name": "Uasya",
            "biography": "Biography"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        genre = Author.objects.last()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(3, Author.objects.count())
        self.assertEqual(['Uasya', 'Biography'], [genre.name, genre.biography])
        self.assertEqual(slugify('Uasya'), response.data['author_slug'])

    # # создание жанра и поля slug, админом
    # def test_post_with_slug(self):
    #     self.assertEqual(2, Author.objects.count())
    #     url = reverse('autor-list')
    #     self.client.force_login(self.user_1)
    #     data = {
    #         "name": "Horror",
    #         "genre_slug": "New slug",
    #         "description": "Horror description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.post(url, data=json_data, content_type='application/json')
    #
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #     self.assertEqual(3, Author.objects.count())
    #     self.assertEqual('New slug', response.data['genre_slug'])
    #
    # # создание жанра без обязательного поля 'name', админом
    # def test_post_without_data(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-list')
    #     self.client.force_login(self.staff)
    #     data = {}
    #     json_data = json.dumps(data)
    #     response = self.client.post(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    #     self.assertEqual('required', response.data['name'][0].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # создание жанра неавторизованным пользователем
    # def test_post_without_login(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-list')
    #
    #     data = {
    #         "name": "Horror",
    #         "description": "Horror description"
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.post(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    #     self.assertEqual('not_authenticated', response.data['detail'].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # создание жанра авторизованным пользователем не админом
    # def test_post_not_staff(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-list')
    #     self.client.force_login(self.user_1)
    #     data = {
    #         "name": "Horror",
    #         "description": "Horror description"
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.post(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    #     self.assertEqual('permission_denied', response.data['detail'].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # создание жанра с не валидными данными, админом
    # def test_post_not_walid(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-list')
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": False,
    #         "description": False
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.post(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    #     self.assertEqual('invalid', response.data['name'][0].code)
    #     self.assertEqual('invalid', response.data['description'][0].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # полное обновление записи
    # def test_put(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Comedy", new_genre.name)
    #     self.assertEqual("Comedy description", new_genre.description)
    #     self.assertEqual(new_genre.slug, response.data['genre_slug'])
    #
    # # полное обновление записи и поля slug
    # def test_put_with_slug(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "genre_slug": "New slug",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertEqual('New slug', response.data['genre_slug'])
    #
    # # полное обновление записи пользователем без логина
    # def test_put_wrong_id(self):
    #     url = reverse('genre-detail', args=(100,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    #
    # # полное обновление записи пользователем без логина
    # def test_put_without_login(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Ужасы", new_genre.name)
    #     self.assertEqual("Описание Ужасы", new_genre.description)
    #
    # # полное обновление записи авторизованным пользователем но без прав админа
    # def test_put_not_staff(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.user_1)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Ужасы", new_genre.name)
    #     self.assertEqual("Описание Ужасы", new_genre.description)
    #
    # # изменение жанра без обязательного поля 'name'
    # def test_put_without_data(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {}
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    #     self.assertEqual('required', response.data['name'][0].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # создание жанра с не валидными данными
    # def test_put_not_walid(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": False,
    #         "description": False
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.put(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    #     self.assertEqual('invalid', response.data['name'][0].code)
    #     self.assertEqual('invalid', response.data['description'][0].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # полное обновление записи
    # def test_patch(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Comedy", new_genre.name)
    #     self.assertEqual("Comedy description", new_genre.description)
    #     self.assertEqual(new_genre.slug, response.data['genre_slug'])
    #
    # # полное обновление записи и поля slug
    # def test_patch_with_slug(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "genre_slug": "New slug",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     self.assertEqual('New slug', response.data['genre_slug'])
    #
    # # полное обновление записи несуществующего жанра
    # def test_patch_wrong_id(self):
    #     url = reverse('genre-detail', args=(100,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    #
    # # полное обновление записи пользователем без логина
    # def test_patch_without_login(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Ужасы", new_genre.name)
    #     self.assertEqual("Описание Ужасы", new_genre.description)
    #
    # # полное обновление записи авторизованным пользователем но без прав админа
    # def test_patch_not_staff(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.user_1)
    #     data = {
    #         "name": "Comedy",
    #         "description": "Comedy description",
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    #     # self.genre_1.refresh_from_db()
    #     new_genre = Genre.objects.get(id=self.genre_1.id)
    #     self.assertEqual("Ужасы", new_genre.name)
    #     self.assertEqual("Описание Ужасы", new_genre.description)
    #
    # # изменение жанра без обязательного поля 'name'
    # def test_patch_without_data(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {}
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #
    # # изменение жанра с не валидными данными
    # def test_patch_not_walid(self):
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     data = {
    #         "name": False,
    #         "description": False
    #     }
    #     json_data = json.dumps(data)
    #     response = self.client.patch(url, data=json_data, content_type='application/json')
    #     self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    #     self.assertEqual('invalid', response.data['name'][0].code)
    #     self.assertEqual('invalid', response.data['description'][0].code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # удаление жанра
    # def test_delete(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.staff)
    #     response = self.client.delete(url)
    #     self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
    #     self.assertEqual(1, Genre.objects.count())
    #
    # # удаление жанра неавторизованным ползователем
    # def test_delete_without_login(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #
    #     response = self.client.delete(url)
    #     self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # удаление жанра пользователем без прав
    # def test_delete_not_staff(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-detail', args=(self.genre_1.id,))
    #     self.client.force_login(self.user_1)
    #     response = self.client.delete(url)
    #     self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    #     self.assertEqual(2, Genre.objects.count())
    #
    # # удаление несуществующего жанра
    # def test_delete_not_exist(self):
    #     self.assertEqual(2, Genre.objects.count())
    #     url = reverse('genre-detail', args=(100,))
    #     self.client.force_login(self.staff)
    #     response = self.client.delete(url)
    #     self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    #     self.assertEqual(2, Genre.objects.count())
    #
