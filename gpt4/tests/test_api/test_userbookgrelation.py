import json

from django.contrib.auth.models import User
from django.test import TestCase

# проверить невозможность нарушения unique_constraint
from django.urls import reverse
from rest_framework import status

from gpt4.models import BookG, UserBookGRelation


class UserBookGRelationApiTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='Tolik')
        self.user_2 = User.objects.create(username='Bolik')

        self.book_1 = BookG.objects.create(title='Book_1', pages=444, content='Book_1 content')
        self.book_2 = BookG.objects.create(title='Book_2', pages=555, content='Book_2 content')

        self.realation = UserBookGRelation.objects.create(book=self.book_1, user=self.user_1, hate_rate=3)

    # проверка добавления лайка
    def test_like(self):
        self.assertFalse(self.realation.like)
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.realation.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(self.realation.like)

    # тест создания записи несуществующей книге
    def test_like_wrong_id(self):
        self.assertFalse(self.realation.like)
        url = reverse('bookg-relation-detail', args=(99,))
        self.client.force_login(self.user_1)
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # проверка возможности поставить лайк неавторизованному пользователю
    def test_without_login(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        data = {
            "like": True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # запрос без данных
    def test_without_data(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {}

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    # проверка изменения рейтинга
    def test_hate_rate(self):
        self.assertEqual(3, self.realation.hate_rate)
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            "hate_rate": 5
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.realation.refresh_from_db()
        self.assertEqual(5, self.realation.hate_rate)

    # создание записи с некорректным значением рейтинга
    def test_hate_rate_wrong(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            "hate_rate": 7
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('invalid_choice', response.data['hate_rate'][0].code)
        self.realation.refresh_from_db()
        self.assertEqual(3, self.realation.hate_rate)

    def test_post_not_allowed(self):
        url = reverse('bookg-relation-detail', args=(self.book_2.id,))
        self.client.force_login(self.user_1)
        data = {}

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_get_detail_not_allowed(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_not_allowed(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

