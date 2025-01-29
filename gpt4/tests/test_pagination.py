from django.test import TestCase


# @classmethod и setUpClass() — это метод класса, который выполняется один раз перед всеми тестами в классе, а не перед
# каждым отдельным тестом. Он используется для подготовки данных или состояния, которые нужны для всех тестов класса
# (например, для дорогих операций, которые не нужно повторять каждый раз).
from django.urls import reverse
from rest_framework import status

from gpt4.models import BookG
from gpt4.utils import cons


class BookGPaginationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(13):
            BookG.objects.create(title=f'Book {i}', pages=f'{i * 50}', content='Some content')

    def test_pagination(self):
        url = reverse('bookg-list')
        response = self.client.get(url, {'page': 1})

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # проверяем общее количество обьектов переданных пагинатору
        self.assertEqual(13, response.data['count'])
        # проверяем количество обьектов на 1 странице
        self.assertEqual(5, len(response.data['results']))
        # проверяем что в ответе есть информация о пагинации
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        # cons(response.data)

    def test_pagination_second_page(self):
        url = reverse('bookg-list')
        response = self.client.get(url, {'page': 2})

        self.assertEqual(5, len(response.data['results']))
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_pagination_third_page(self):
        url = reverse('bookg-list')
        response = self.client.get(url, {'page': 3})

        self.assertEqual(3, len(response.data['results']))
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_custom_page_size(self):
        url = reverse('bookg-list')
        response = self.client.get(url, {'page': 2, 'page_size': 6})

        self.assertEqual(6, len(response.data['results']))
        self.assertIsNotNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])