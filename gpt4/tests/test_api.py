from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Count, Case, When, IntegerField, F
from django.test import TestCase
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail

from gpt4.models import Author, BookG, Genre, UserBookGRelation, Review
from gpt4.serializers import BookGSerializer, UserSerializer, ReviewSerializer

from django.test.utils import CaptureQueriesContext

from gpt4.utils import cons


class BookGApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Kroks')
        self.user_2 = User.objects.create(username='Fedya')
        self.user_3 = User.objects.create(username="I'm Boss", is_staff=True)

        self.author_1 = Author.objects.create(name='Teon')
        self.author_2 = Author.objects.create(name='Kreon')
        self.author_3 = Author.objects.create(name='Foton')

        self.genre_1 = Genre.objects.create(name='Horror')
        self.genre_2 = Genre.objects.create(name='Documental')

        self.book_1 = BookG.objects.create(title='Everest', author=self.author_1,
                                           owner=self.user_1, pages=300, content='content1')
        self.book_2 = BookG.objects.create(title='Elbrus Tom 1', author=self.author_2,
                                           owner=self.user_1, pages=250, content='content2')
        self.book_3 = BookG.objects.create(title='Gora', author=self.author_2, pages=300, content='content3 Tom 1')
        self.book_4 = BookG.objects.create(title='Foton Book', author=self.author_3, pages=270, content='content3')

        self.review_1 = Review.objects.create(user=self.user_1, book=self.book_1, rating=5, content='content')
        self.review_2 = Review.objects.create(user=self.user_2, book=self.book_1, rating=4, content='content FFF')

    # проверка получения списка книг
    def test_get_list(self):
        url = reverse('bookg-list')

        # чтобы проверить сколько запросов происходит во время запроса, запустим response в контексте
        # CaptureQueriesContext — инструмент Django для мониторинга SQL-запросов, а connection — это
        # объект подключения к базе данных, будет логировать все SQL-зарпоссы во время его работы
        with CaptureQueriesContext(connection) as queries:
            # client это тестовый клиент для имитации http запросов к приложению в тестах, get - get запрос
            response = self.client.get(url)
            self.assertEqual(2, len(queries))


        # response = self.client.get(url)

        books = BookG.objects.annotate(annotated_likes=Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                                     owner_name=F('owner__username')).select_related('owner').prefetch_related('genres').order_by('id')

        context = {'request': response.wsgi_request}  # Получаем объект запроса

        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON,
        # валидирует данные на вход а на выхо создвёт словарь из модели
        serializer_data = BookGSerializer(books, context=context, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # пповерка получения книги по её id
    def test_get_detail(self):
        url = reverse('bookg-detail', args=(self.book_1.id,))
        response = self.client.get(url)

        data = BookG.objects.filter(id=self.book_1.id).annotate(annotated_likes=
                   Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                   owner_name=F('owner__username')).select_related('owner').prefetch_related('genres')[0]
        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON,
        # валидирует данные на вход а на выхо создвёт словарь из модели

        context = {'request': response.wsgi_request}  # Получаем объект запроса

        serializer_data = BookGSerializer(data, context=context).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка ответа при запросе несуществующей книги
    def test_not_exist(self):
        url = reverse('bookg-detail', args=(30,))
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual('not_found', response.data['detail'].code)

    # проверка создания книги
    def test_create(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('bookg-list')
        self.client.force_login(self.user_1)
        data = {
            "title": "Book Uebuc",
            "author": self.author_2.id,
            "pages": 550,
            "content": "Book ochin interecny!",
            "genres": [self.genre_1.id, self.genre_2.id]
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        book = BookG.objects.get(content='Book ochin interecny!')
        book_genres = list(book.genres.values_list('id', flat=True))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual([self.genre_1.id, self.genre_2.id], book_genres)
        self.assertEqual(5, BookG.objects.count())
        self.assertEqual(self.author_2, book.author)

    # проверка создания книги с несуществующим автором
    def test_create_not_valid(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('bookg-list')
        self.client.force_login(self.user_1)
        data = {
            "title": "Super Book",
            "author": 30,
            "pages": 200,
            "content": "Super content"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type="application/json")

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual([ErrorDetail(string='Invalid pk "30" - object does not exist.', code='does_not_exist')], response.data['author'])
        self.assertEqual(4, BookG.objects.count())

    # проверка создания книги без заголовка
    def test_create_without_field(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('bookg-list')
        self.client.force_login(self.user_1)
        data = {
            "pages": 200,
            "content": "Super content"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual([ErrorDetail(string='This field is required.', code='required')], response.data['title'])
        self.assertEqual(4, BookG.objects.count())

    # проверка на создание книги неавторизованному пользователю
    def test_create_without_login(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('bookg-list')

        data = {
            "title": "Book Uebuc",
            "author": self.author_2.id,
            "pages": 550,
            "content": "Book ochin interecny!",
            "genres": [self.genre_1.id, self.genre_2.id]
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)
        self.assertEqual(4, BookG.objects.count())

    # проверка попытки создания пустой записи
    def test_create_without_data(self):
        url = reverse('bookg-list')
        self.client.force_login(self.user_1)
        data = {}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn('required', response.data['title'][0].code)
        self.assertIn('required', response.data['content'][0].code)
        self.assertIn('required', response.data['pages'][0].code)

    # проверка полного обновления книги
    def test_update(self):
        url = reverse('bookg-detail', args=(self.book_2.id,))
        self.client.force_login(self.user_1)
        data = {
            "title": "Change",
            "author": self.author_1.id,
            "pages": 1000,
            "content": "Content New"
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.book_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("Change", self.book_2.title)
        self.assertEqual(self.author_1, self.book_2.author)
        self.assertEqual(1000, self.book_2.pages)
        self.assertEqual('Content New', self.book_2.content)

    # проверка частичного обновления книги
    def test_partial_update(self):
        url = reverse('bookg-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            "title": "Soroconozhka",
            "author": self.author_2.id,
            "owner": self.user_2.id,
            "pages": 250,
            "content": "Soroconozhka"
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type="application/json")

        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("Soroconozhka", self.book_1.title)
        self.assertEqual(self.author_2, self.book_1.author)
        self.assertEqual(self.user_1.username, self.book_1.owner.username)
        self.assertEqual(250, self.book_1.pages)
        self.assertEqual("Soroconozhka", self.book_1.content)

    # проверка возможности редактировать чужую запись
    def test_update_not_own(self):
        url = reverse('bookg-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_2)
        data = {
            "title": "Soroconozhka"
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # так как юзер авторизован то выкинет ошибку доступа
        self.assertEqual('permission_denied', response.data['detail'].code)

    # проверка удаления книги
    def test_delete(self):
        self.assertEqual(True, BookG.objects.filter(id=self.book_1.id).exists())
        url = reverse('bookg-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        # cons(response.status_code)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(False, BookG.objects.filter(id=self.book_1.id).exists())

    # проверка удаления чужой книги
    def test_delete_not_owner(self):
        url = reverse('bookg-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_2)
        response = self.client.delete(url)
        # cons(response.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # проверка удаления чужой книги с аккаунта персонала
    def delete_not_owner_but_staff(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('bookg-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_3)  # is_staff
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, BookG.objects.count())

    # проверка фильтрации книг c помошью кастомного фильтра FilterSet
    def test_filter(self):
        url = reverse('bookg-list')
        response = self.client.get(url, data={'min_pages': 250, 'max_pages': 270})

        books = BookG.objects.filter(id__in=[self.book_2.id, self.book_4.id]).annotate(annotated_likes=
                     Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                     owner_name=F('owner__username')).select_related('owner').prefetch_related('genres')

        context = {'request': response.wsgi_request}  # Получаем объект запроса

        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON, а просто готовит их для дальнейшего
        # использования (например, для отправки на клиент).
        serializer_data = BookGSerializer(books, context=context, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка кастомного фильтра FilterSet на невалидные значения
    def test_filter_bad_field(self):
        url = reverse('bookg-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url, data={'min_pages': 'one', 'max_pages': 'two'})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('invalid', response.data['min_pages'][0].code)
        self.assertEqual('invalid', response.data['max_pages'][0].code)

    # проверка работы кастомного фильтра BookGFilterBackends(BaseFilterBackend)
    def test_filter_custom_backends(self):
        url = reverse('bookg-list')
        response = self.client.get(url, data={'author_imya': 'Foton'})

        book = BookG.objects.filter(id=self.book_4.id).annotate(annotated_likes=
                                    Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                                    owner_name=F('owner__username')).select_related('owner').prefetch_related('genres')

        # Контекст с объектом request: Ты добавил context={'request': response.wsgi_request},
        # что решает проблему с генерацией полных URL в тестах. по сути просто передаётся http://testserver в request
        # что позволяет корректно сформировать урлы к связанным моделям
        context = {'request': response.wsgi_request}  # Получаем объект запроса

        serializer_data = BookGSerializer(book, context=context, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_filter_invalid_params(self):
        url = reverse('bookg-list')
        response = self.client.get(url, data={'author_imya': 3})
        self.assertEqual([], response.data)

    # проверка работы поиска через django_filters
    def test_search(self):
        url = reverse('bookg-list')
        response = self.client.get(url, data={'search': 'Tom 1'})
        books = BookG.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(annotated_likes=
                     Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                     owner_name=F('owner__username')).select_related('owner').prefetch_related('genres')

        # Контекст с объектом request: Ты добавил context={'request': response.wsgi_request},
        # что решает проблему с генерацией полных URL в тестах. по сути просто передаётся http://testserver в request
        # что позволяет корректно сформировать урлы к связанным моделям
        context = {'request': response.wsgi_request}  # Получаем объект запроса

        serializer_data = BookGSerializer(books, context=context, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка сортировки через django_filters
    def test_ordering(self):
        url = reverse('bookg-list')
        response = self.client.get(url, data={'ordering': '-id'})

        books = BookG.objects.annotate(annotated_likes=
                     Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                     owner_name=F('owner__username')).select_related('owner').prefetch_related('genres').order_by('-id')

        context = {'request': response.wsgi_request}  # Получаем объект запроса

        serializer_data = BookGSerializer(books, context=context, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

                                             # bookg/  ACTIONS
    # получение записей через гет запрос
    def test_get_review(self):
        url = reverse('bookg-review', args=(self.book_1.id,))
        response = self.client.get(url)
        revs = Review.objects.filter(book_id=self.book_1.id)
        serializer_data = ReviewSerializer(revs, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение записей по неправильному id
    def test_get_review_wrong_id(self):
        url = reverse('bookg-review', args=(99,))
        response = self.client.get(url)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # ПРОВЕРКИ НЕДОПУСТИМЫХ МЕТОДОВ

    def test_post_not_allowed(self):
        url = reverse('bookg-review', args=(self.book_2.id,))
        self.client.force_login(self.user_1)
        data = {}

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_patch_not_allowed(self):
        url = reverse('bookg-review', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.patch(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_put_not_allowed(self):
        url = reverse('bookg-review', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_not_allowed(self):
        url = reverse('bookg-review', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)



    def tearDown(self) -> None:
        User.objects.all().delete()
        Author.objects.all().delete()
        BookG.objects.all().delete()
        Genre.objects.all().delete()
        super().tearDown()


# проверить невозможность нарушения unique_constraint
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

    def test_get_not_allowed(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_not_allowed(self):
        url = reverse('bookg-relation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)


    def tearDown(self) -> None:
        User.objects.all().delete()
        BookG.objects.all().delete()
        UserBookGRelation.objects.all().delete()
        super().tearDown()


class UserApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='User_1', first_name='Kri')
        self.user_2 = User.objects.create(username='User_2', first_name='Fox')
        self.admin = User.objects.create(username='Boss', first_name='Teon', last_name='Ko', is_staff=True)

        self.book_1 = BookG.objects.create(title='Book_1', pages=444, owner=self.user_1, content='Book_1 content')
        self.book_2 = BookG.objects.create(title='Book_2', pages=555, owner=self.user_1, content='Book_2 content')

    # получение данных юзера с правами администратора
    def test_detail(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = UserSerializer(self.user_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение несуществующего пользователя
    def test_detail_wrong_user(self):
        url = reverse('user-detail', args=(100,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # получение данных юиера без прав администратора
    def test_get_detail_not_staff(self):
        url = reverse('user-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # получение списка юзеров с правами администратора
    def test_get_list(self):
        url = reverse('user-list')
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = UserSerializer(User.objects.all(), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка юзеров без прав админа
    def test_get_list_not_staff(self):
        url = reverse('user-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # получение списка связанных книг хозяином
    def test_get_action_owner(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка ужих связанных книг
    def test_get_action_not_own(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_2)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # получение списка связанных книг админом
    def test_get_action_staff(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


    # ПРОВЕРКИ НЕДОПУСТИМЫХ МЕТОДОВ

    def test_post_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        data = {}

        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_patch_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.patch(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_put_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_delete_not_allowed(self):
        url = reverse('user-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)
