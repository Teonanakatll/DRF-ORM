from django.core.exceptions import ValidationError
from django.test import TestCase
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from gpt4.models import Author, BookG, Genre, UserBookGRelation, Review
from gpt4.serializers import BookGSerializer, UserSerializer
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

    # проверка получения списка книг
    def test_get_list(self):
        url = reverse('my-list')
        response = self.client.get(url)

        books = BookG.objects.all()
        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON, а просто готовит их для дальнейшего
        # использования (например, для отправки на клиент).
        serializer_data = BookGSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # пповерка получения книги по её id
    def test_get_detail(self):
        url = reverse('my-detail', args=(self.book_1.id,))
        response = self.client.get(url)

        data = BookG.objects.get(id=self.book_1.id)
        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON, а просто готовит их для дальнейшего
        # использования (например, для отправки на клиент).
        serializer_data = BookGSerializer(data).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка ответа при запросе несуществующей книги
    def test_not_exist(self):
        url = reverse('my-detail', args=(3,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # проверка создания книги
    def test_create(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('my-list')
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
        book = BookG.objects.last()
        book_genres = list(book.genres.values_list('id', flat=True))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual([self.genre_1.id, self.genre_2.id], book_genres)
        self.assertEqual(5, BookG.objects.count())
        self.assertEqual(self.author_2, BookG.objects.last().author)

    # проверка создания книги с несуществующим автором
    def test_create_not_valid(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('my-list')
        self.client.force_login(self.user_1)
        data = {
            "title": "Super Book",
            "author": 1,
            "pages": 200,
            "content": "Super content"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('does_not_exist', response.data['author'][0].code)
        self.assertEqual(4, BookG.objects.count())

    # проверка создания книги без заголовка
    def test_create_without_field(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('my-list')
        self.client.force_login(self.user_1)
        data = {
            "pages": 200,
            "content": "Super content"
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(4, BookG.objects.count())

    # проверка на создание книги неавторизованному пользователю
    def test_create_without_login(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('my-list')
        # self.client.force_login(self.user_1)
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
        url = reverse('my-list')
        self.client.force_login(self.user_1)
        data = {}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertIn('title', response.data)
        self.assertIn('content', response.data)
        self.assertIn('pages', response.data)

    # проверка полного обновления книги
    def test_update(self):
        url = reverse('my-detail', args=(self.book_2.id,))
        self.client.force_login(self.user_1)
        data = {
            "title": "Change",
            "author": self.book_2.author.id,
            "pages": self.book_2.pages,
            "content": "Content"
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.book_2.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("Change", self.book_2.title)

    # проверка частичного обновления книги
    def test_partial_update(self):
        url = reverse('my-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            "title": "Soroconozhka"
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type="application/json")

        self.book_1.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("Soroconozhka", self.book_1.title)

    # проверка возможности редактировать чужую запись
    def test_update_not_own(self):
        url = reverse('my-detail', args=(self.book_1.id,))
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
        url = reverse('my-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.delete(url)
        # cons(response.status_code)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(False, BookG.objects.filter(id=self.book_1.id).exists())

    # проверка удаления чужой книги
    def test_delete_not_owner(self):
        url = reverse('my-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_2)
        response = self.client.delete(url)
        # cons(response.status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # проверка удаления чужой книги с аккаунта персонала
    def delete_not_owner_but_staff(self):
        self.assertEqual(4, BookG.objects.count())
        url = reverse('my-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_3)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, BookG.objects.count())

    # проверка фильтрации книг c помошью кастомного фильтра FilterSet
    def test_filter(self):
        url = reverse('my-list')
        response = self.client.get(url, data={'min_pages': 250, 'max_pages': 270})

        books = BookG.objects.filter(id__in=[self.book_2.id, self.book_4.id])
        # Этот вызов сериализует данные (в данном случае books), но возвращает Python-объект (список или словарь).
        # Сериализатор сам по себе не превращает эти данные в строку JSON, а просто готовит их для дальнейшего
        # использования (например, для отправки на клиент).
        serializer_data = BookGSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка кастомного фильтра FilterSet на невалидные значения
    def test_filter_bad_field(self):
        url = reverse('my-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url, data={'min_pages': 'one', 'max_pages': 'two'})
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual('invalid', response.data['min_pages'][0].code)
        self.assertEqual('invalid', response.data['max_pages'][0].code)

    # проверка работы кастомного фильтра filter_backends
    def test_filter_custom_backends(self):
        url = reverse('my-list')
        response = self.client.get(url, data={'author_imya': 'Foton'})
        serializer_data = BookGSerializer([self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # def test_filter_invalid_params(self):

    # проверка работы поиска через django_filters
    def test_search(self):
        url = reverse('my-list')
        response = self.client.get(url, data={'search': 'Tom 1'})
        books = BookG.objects.filter(id__in=[self.book_2.id, self.book_3.id])
        serializer_data = BookGSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # проверка сортировки через django_filters
    def test_ordering(self):
        url = reverse('my-list')
        response = self.client.get(url, data={'ordering': '-id'})
        serializer_data = BookGSerializer([self.book_4, self.book_3, self.book_2, self.book_1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

                                             #  ACTIONS
    # создание рецензии через экщен
    def test_post_review(self):
        self.assertEqual(1, Review.objects.count())
        url = reverse('my-review', args=(self.book_2.id,))
        self.client.force_login(self.user_1)
        data = {
            "content": "content",
            "rating": 10,
            "is_annonymous": True
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, Review.objects.count())

        with self.assertRaises(ValidationError):
            self.client.post(url, data=json_data, content_type='application/json')


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
        url = reverse('my_rel-detail', args=(self.book_1.id,))
        self.client.force_login(self.user_1)
        data = {
            'like': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.realation.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(self.realation.like)

    # проверка возможности поставить лайк неавторизованному пользователю
    def test_without_login(self):
        url = reverse('my_rel-detail', args=(self.book_1.id,))
        data = {
            "like": True
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual('not_authenticated', response.data['detail'].code)

    # проверка что нельзя изменить несвой лайк
    def test_hate_rate(self):
        self.assertEqual(3, self.realation.hate_rate)
        url = reverse('my_rel-detail', args=(self.book_1.id,))
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
        url = reverse('my_rel-detail', args=(self.book_1.id,))
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
        url = reverse('users-detail', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = UserSerializer(self.user_1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение несуществующего пользователя
    def test_detail_wrong_user(self):
        url = reverse('users-detail', args=(100,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    # получение данных юиера без прав администратора
    def test_get_detail_not_staff(self):
        url = reverse('users-detail', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('permission_denied', response.data['detail'].code)

    # получение списка юзеров с правами администратора
    def test_get_list(self):
        url = reverse('users-list')
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = UserSerializer(User.objects.all(), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка юзеров без прав админа
    def test_get_list_not_staff(self):
        url = reverse('users-list')
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # получение списка связанных книг хозяином
    def test_get_action_owner(self):
        url = reverse('users-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_1)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # получение списка ужих связанных книг
    def test_get_action_not_own(self):
        url = reverse('users-list-books', args=(self.user_1.id,))
        self.client.force_login(self.user_2)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # получение списка связанных книг админом
    def test_get_action_staff(self):
        url = reverse('users-list-books', args=(self.user_1.id,))
        self.client.force_login(self.admin)
        response = self.client.get(url)
        serializer_data = BookGSerializer(BookG.objects.filter(owner_id=self.user_1.id), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
