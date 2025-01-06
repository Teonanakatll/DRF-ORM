import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from gpt4.models import Author, BookG
from gpt4.serializers import BookGSerializer
from gpt4.utils import cons


class BookGApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Kroks')

        self.author_1 = Author.objects.create(name='Teon')
        self.author_2 = Author.objects.create(name='Kreon')

        self.book_1 = BookG.objects.create(title='Everest', author=self.author_1, pages=300, content='content1')
        self.book_2 = BookG.objects.create(title='Elbrus', author=self.author_2, pages=250, content='content2')
        self.book_3 = BookG.objects.create(title='Gora', author=self.author_2, pages=300, content='content3')

        self.data = ''


    def t_get_list(self):
        url = reverse('my-list')
        response = self.client.get(url)

        books = BookG.objects.all()
        serializer_data = BookGSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

        queryset = ''
        expected_json_data = ''

        # 1. assertIn и assertNotIn
        # Эти методы проверяют, содержится ли элемент в каком-либо контейнере (список, словарь, строка и т. д.).
        self.assertIn('foo', response.data)  # Проверяет, что 'foo' есть в response.data
        self.assertNotIn('bar', response.data)  # Проверяет, что 'bar' нет в response.data

        # 2. assertIsNone и assertIsNotNone
        # Эти методы проверяют, равен ли объект None или не равен ему.
        self.assertIsNone(response.data.get('error'))  # Проверяет, что ключ 'error' не существует в response.data
        self.assertIsNotNone(response.data.get('result'))  # Проверяет, что 'result' существует

        # 3. assertIsInstance
        # Проверяет является ли обьект экземпляром указанного класса
        self.assertIsInstance(response, HttpResponse)  # Проверяет, что ответ является экземпляром HttpResponse

        # 4. assertRaises
        # Используется для проверки, что код вызывает исключение. Этот метод полезен для тестирования обработки ошибок.
        with self.assertRaises(ValueError):  # Проверка на выброс исключения ValueError
            self.client.post(url, data=self.data)

        # 5. assertContains и assertNotContains
        # Проверяет, содержится ли определённая строка в содержимом HTTP-ответа.
        self.assertContains(response, 'Book Uebuc')  # Проверяет, что 'Book Uebuc' есть в response.content
        self.assertNotContains(response, 'error')  # Проверяет, что 'error' нет в response.content

        # 7. assertEqual с округлением
        # Если сравниваешь числа с плавающей точкой, можно использовать assertAlmostEqual, чтобы избежать проблем с точностью:
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=1)  # Проверяет, что результат округлен до 1 знака после запятой

        # 8. assertCountEqual
        # Проверяет, что два списка содержат одинаковые элементы, без учета порядка.
        self.assertCountEqual([1, 2, 3], [3, 2, 1])  # Проверяет, что списки содержат одинаковые элементы

        # 9. assertQuerysetEqual
        # Этот метод помогает проверять, что набор данных (QuerySet) в базе данных соответствует ожидаемому.

        self.assertQuerysetEqual(
            queryset,
            ['<Expected Object>', '<Another Expected Object>'])  # Сравнивает QuerySet с ожидаемыми объектами

        # 12. assertJSONEqual
        # В Django REST Framework ты можешь использовать этот метод для проверки, что ответ в формате JSON соответствует ожидаемому.
        self.assertJSONEqual(response.content, expected_json_data)