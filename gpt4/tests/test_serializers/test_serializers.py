import glob
import os
import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count, Case, When, IntegerField, F
from django.test import TestCase
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from django.urls import reverse
from django.utils import timezone
from slugify import slugify

from books import settings
from gpt4.models import Author, BookG, Genre, UserBookGRelation, Review, BookGenre
from gpt4.serializers import BookGSerializer, UserBookGRelationSerializer, UserSerializer, BookGLinkSerializer, \
    GenreLinkSerializer, ReviewSerializer, AuthorSerializer, GenreSerializer
from gpt4.utils import cons

def today():
    today_string = str(timezone.now().date())
    return datetime.strptime(today_string, '%Y-%m-%d').date()

def create_test_image(image_name):
    """Создаёт временное изображение и сохраняет его в MEDIA_ROOT, нужно передать имя с расширением"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, dir=f'{settings.MEDIA_ROOT}')

    image = Image.new('RGB', (100, 100), color=(255, 0, 0))
    image.save(temp_file, format='JPEG')
    temp_file.close()  # Закрываем, чтобы можно было открыть через `open()`

    # Путь к файлу
    file_path = temp_file.name

    # нужно передать имя с расширением в SimpleUploadedFile, чтобы он корректно определил тип файла.
    with open(file_path, 'rb') as f:
        # имитирует загруженный файл, как если бы он был загружен через форму в Django.
        # Этот объект SimpleUploadedFile имитирует поведение реального загруженного
        # файла и может быть сохранён в базу данных, если передать его в модель.
        # это функциональность класса, а не экземпляра.
        uploaded_file = SimpleUploadedFile(image_name, f.read(), content_type='image/jpeg')

    return uploaded_file, file_path


def tearDownFilesAndObjects(model_classes, file_paths):
    """
    Удаляет временные файлы и объекты модели после теста.

    :param model_class: Класс модели, объекты которой нужно удалить.
    :param file_paths: Список путей к файлам, которые нужно удалить.
    """
    # Удаляем файлы
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                # cons(f"Файл {file_path} успешно удалён.")
            except OSError as e:
                cons(f"Ошибка при удалении файла {file_path}: {e}")

    # Удаляем объекты модели, если instance передан
    if model_classes:
        for model in model_classes:
            model.objects.all().delete()
            # cons(f"Объекты {model.__name__} успешно удалены.")

class BookGSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.author_1 = Author.objects.create(name='Teon')
        self.author_2 = Author.objects.create(name='Kreon')

        self.user_1 = User.objects.create(username='Fedya')
        self.user_2 = User.objects.create(username='Boris')

        self.genre_1 = Genre.objects.create(name='Триллер')
        self.genre_2 = Genre.objects.create(name='Комедия')

        # Создание изображений и их путей
        self.image_1, image_path_1 = create_test_image('image1.jpg')
        self.image_2, image_path_2 = create_test_image('image2.jpg')

        # Сохраняем пути файлов для удаления в tearDown
        self.test_files = [image_path_1, image_path_2]


        self.book_1 = BookG.objects.create(title='Еверест', author=self.author_1, cover=self.image_1,
                                                                       owner=self.user_1, pages=300, content='content1')
        self.book_1.genres.set([self.genre_1, self.genre_2])
        self.book_2 = BookG.objects.create(title='Ельбрус', author=self.author_2, cover=self.image_2,
                                                                       owner=self.user_2, pages=250, content='content2')

        self.relation_1 = UserBookGRelation.objects.create(book=self.book_1, user=self.user_1, like=True, hate_rate=5)
        self.relation_2 = UserBookGRelation.objects.create(book=self.book_1, user=self.user_2, like=True, hate_rate=2)
        self.relation_3 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_1)
        self.relation_4 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_2, like=True, hate_rate=5)

    def tearDown(self) -> None:
        # Используем универсальную функцию для удаления
        tearDownFilesAndObjects([BookG], self.test_files)

    # @staticmethod — это декоратор в Python, который используется для обозначения метода, который не зависит от
    # экземпляра класса (не имеет доступа к атрибутам или методам объекта)
    # Статический метод — это метод, который не работает с экземпляром объекта (не имеет self в качестве
    # первого аргумента) и не может изменять его состояние.
    # @staticmethod

    def test_ok_bookg_serializer(self):
        books = BookG.objects.annotate(annotated_likes=Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                                     owner_name=F('owner__username')).select_related('owner').prefetch_related('genres').order_by('id')

        # HyperlinkedRelatedField требует наличия объекта request в контексте, чтобы корректно генерировать URL.
        # Когда ты создаёшь сериализатор, нужно передавать request в контекст. Это важно для корректного формирования
        # ссылок через HyperlinkedIdentityField или HyperlinkedRelatedField.
        url = reverse('bookg-detail', args=(self.book_1.id,))  # Ссылку на список книг или детали книги
        response = self.client.get(url)

        # Контекст с объектом request: Ты добавил context={'request': response.wsgi_request},
        # что решает проблему с генерацией полных URL в тестах. по сути просто передаётся http://testserver в request
        # что позволяет корректно сформировать урлы к связанным моделям
        context = {'request': response.wsgi_request}  # Получаем объект запроса

        data = BookGSerializer(books, context=context, many=True).data


        expected_data = [
            {
                "id": self.book_1.id,
                "title": "Еверест",
                "book_slug": slugify("Еверест"),
                "cover_url": f"http://testserver/media/{self.book_1.cover.name}",
                "content": "content1",
                "author_name": "Teon",
                "author_slug": slugify(self.author_1.name),
                "author_url": f"http://testserver{reverse('author-detail', args=(self.author_1.id,))}",
                "owner_name": "Fedya",
                "pages": 300,
                "annotated_likes": 2,
                "avg_hate_rate": '3.50',
                "view_created_at": today(),
                "genres": [
                    {
                        "id": self.genre_1.id,
                        "name": "Триллер",
                        "genre_slug": slugify("Триллер"),
                        "genre_url": f"http://testserver{reverse('genre-detail', args=(self.genre_1.id,))}"
                    },
                    {
                        "id": self.genre_2.id,
                        "name": "Комедия",
                        "genre_slug": slugify("Комедия"),
                        "genre_url": f"http://testserver{reverse('genre-detail', args=(self.genre_2.id,))}"
                    }
                ]
            },
            {
                "id": self.book_2.id,
                "title": "Ельбрус",
                "book_slug": slugify("Ельбрус"),
                "cover_url": f"http://testserver/media/{self.book_2.cover.name}",
                "content": "content2",
                "author_name": "Kreon",
                "author_slug": slugify(self.author_2.name),
                "author_url": f"http://testserver{reverse('author-detail', args=(self.author_2.id,))}",
                "owner_name": "Boris",
                "pages": 250,
                "annotated_likes": 1,
                "avg_hate_rate": '2.50',
                "view_created_at": today(),
                "genres": []
            }
        ]
        # cons(expected_data)
        # cons(data)
        self.assertEqual(expected_data, data)


class BookGLinkSerializerTestCase(TestCase):
    def setUp(self) -> None:
        # Создание изображений и их путей
        self.image_1, self.path_image_1 = create_test_image('image1.jpg')
        self.image_2, self.path_image_2 = create_test_image('image2.jpg')

        # Сохраняем пути файлов для удаления в tearDown
        self.test_files = [self.path_image_1, self.path_image_2]

        self.book_1 = BookG.objects.create(title='Еверест', cover=self.image_1, content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Ельбрус', cover=self.image_2, content='Content Book_2', pages=300)

        self.base_url = "http://testserver"

    def tearDown(self) -> None:
        tearDownFilesAndObjects([BookG], self.test_files)

    # проверка встроенного сериализатора который в сер. GenreSerializer выводит список связанных книг с сылками
    def test_ok_bookglink_serializer(self):
        response = self.client.get(reverse('bookg-list'))
        context = {'request': response.wsgi_request}

        data = BookGLinkSerializer([self.book_1, self.book_2], context=context, many=True).data

        expected_data = [
            {
                "id": self.book_1.id,
                "title": "Еверест",
                "book_slug": slugify("Еверест"),
                "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
            },
            {
                "id": self.book_2.id,
                "title": "Ельбрус",
                "book_slug": slugify("Ельбрус"),
                "cover_url": f'http://testserver/media/{self.book_2.cover.name}',
                "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_2.id,))}"
            }
        ]
        # cons(expected_data)
        # cons(data)
        self.assertEqual(expected_data, data)


class GenreLinkSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.genre_1 = Genre.objects.create(name='Ужасы')
        self.genre_2 = Genre.objects.create(name='Триллер')
        # cons(self.genre_1, self.genre_2)
        self.base_url = 'http://testserver'

    def test_ok_genrelink_serializer(self):
        response = self.client.get(reverse('genre-list'))
        context = {'request': response.wsgi_request}
        data = GenreLinkSerializer([self.genre_1, self.genre_2], context=context, many=True).data

        expected_data = [
            {
                "id": self.genre_1.id,
                "name": "Ужасы",
                "genre_slug": slugify("Ужасы"),
                "genre_url": f"{self.base_url}{reverse('genre-detail', args=(self.genre_1.id,))}"
            },
            {
                "id": self.genre_2.id,
                "name": "Триллер",
                "genre_slug": slugify("Триллер"),
                "genre_url": f"{self.base_url}{reverse('genre-detail', args=(self.genre_2.id,))}"
            }
        ]
        self.assertEqual(expected_data, data)


class GenreSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.genre_1 = Genre.objects.create(name='Ужасы', description='Описание Ужасы')
        self.genre_2 = Genre.objects.create(name='Триллер', description='Описание Триллер')
        self.genre_3 = Genre.objects.create(name='Комедия', description='Описание Комедия')

        self.image_1, self.path_image_1 = create_test_image('image1.jpg')
        self.image_2, self.path_image_2 = create_test_image('image2.jpg')
        self.test_files = [self.path_image_1, self.path_image_2]

        self.book_1 = BookG.objects.create(title='Еверест', cover=self.image_1, content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Ельбрус', cover=self.image_2, content='Content Book_2', pages=300)

        self.bookgenre_1 = BookGenre.objects.create(book=self.book_1, genre=self.genre_1)
        self.bookgenre_3 = BookGenre.objects.create(book=self.book_1, genre=self.genre_2)
        self.bookgenre_4 = BookGenre.objects.create(book=self.book_2, genre=self.genre_1)

        self.base_url = "http://testserver"

    def tearDown(self) -> None:
        tearDownFilesAndObjects([BookG], self.test_files)

    def test_ok_genre_serializer(self):
        response = self.client.get(reverse('genre-list'))
        context = {"request": response.wsgi_request}

        data = GenreSerializer([self.genre_1, self.genre_2, self.genre_3], context=context, many=True).data

        expected_data = [
            # 'id', 'name', 'description', 'book_list'
            {
                "id": self.genre_1.id,
                "name": "Ужасы",
                "genre_slug": slugify("Ужасы"),
                "description": "Описание Ужасы",
                "book_list": [
                    {
                        "id": self.book_1.id,
                        "title": "Еверест",
                        "book_slug": slugify("Еверест"),
                        "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
                    },
                    {
                        "id": self.book_2.id,
                        "title": "Ельбрус",
                        "book_slug": slugify("Ельбрус"),
                        "cover_url": f'http://testserver/media/{self.book_2.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_2.id,))}"
                    }
                ]
            },
            {
                "id": self.genre_2.id,
                "name": "Триллер",
                "genre_slug": slugify("Триллер"),
                "description": "Описание Триллер",
                "book_list": [
                    {
                        "id": self.book_1.id,
                        "title": "Еверест",
                        "book_slug": slugify("Еверест"),
                        "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
                    }
                ]
            },
            {
                "id": self.genre_3.id,
                "name": "Комедия",
                "genre_slug": slugify("Комедия"),
                "description": "Описание Комедия",
                "book_list": []
            }
        ]
        self.assertEqual(expected_data, data)
        # cons(data)


class UserBookGRelationSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Teon', is_staff=True)

        self.book_1 = BookG.objects.create(title='Book_1', content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Book_2', content='Content Book_2', pages=300)

        self.relation_1 = UserBookGRelation.objects.create(book=self.book_1, like=True, in_bookmarks=True, hate_rate=3)
        self.relation_2 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_1, hate_rate=5)

    def test_ok_userbookgrelation_serializer(self):
        relations = UserBookGRelation.objects.all()
        data = UserBookGRelationSerializer(relations, many=True).data

        expected_data = [
            {
                "id": self.relation_1.id,
                "book": self.relation_1.book_id,
                "user": None,
                "like": True,
                "in_bookmarks": True,
                "hate_rate": 3
            },
            {
                "id": self.relation_2.id,
                "book": self.relation_2.book_id,
                "user": self.user_1.id,
                "like": False,
                "in_bookmarks": False,
                "hate_rate": 5
            }
        ]

        self.assertEqual(expected_data, data)


class UserSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.image_1, self.path_image_1 = create_test_image('image1.jpg')
        self.image_2, self.path_image_2 = create_test_image('image2.jpg')
        self.test_files = [self.path_image_1, self.path_image_2]

        self.book_1 = BookG.objects.create(title='Еверест', cover=self.image_1, content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Ельбрус', cover=self.image_1, content='Content Book_2', pages=300)
        self.book_3 = BookG.objects.create(title='Казбек', cover=self.image_2, content='Content Book_3', pages=400)
        self.book_4 = BookG.objects.create(title='Аннапурна', cover=self.image_2, content='Content Book_4', pages=500)

        self.user_1 = User.objects.create(username='Boss', first_name='Teon', last_name='Ko', is_staff=True)
        self.user_2 = User.objects.create(username='User', first_name='Kri')

        self.user_1.owner_books.set([self.book_1, self.book_2])
        self.user_1.readers_books.set([self.book_3, self.book_4])

        self.user_2.owner_books.set([self.book_3, self.book_4])
        self.user_2.readers_books.set([self.book_1, self.book_2])

        self.base_url = "http://testserver"

    def tearDown(self) -> None:
        tearDownFilesAndObjects([BookG], self.test_files)

    def test_ok_user_serializer(self):
        url = reverse('user-list')
        response = self.client.get(url)
        context = {'request': response.wsgi_request}

        users = User.objects.prefetch_related('owner_books', 'readers_books').all()
        data = UserSerializer(users, context=context, many=True).data
        # cons(data)

        expected_data = [
            {
                "id": self.user_1.id,
                "username": "Boss",
                "first_name": "Teon",
                "last_name": "Ko",
                "is_staff": True,
                "my_books": [
                    {
                        "id": self.book_1.id,
                        "title": "Еверест",
                        "book_slug": slugify("Еверест"),
                        "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
                    },
                    {
                        "id": self.book_2.id,
                        "title": "Ельбрус",
                        "book_slug": slugify("Ельбрус"),
                        "cover_url": f'http://testserver/media/{self.book_2.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_2.id,))}"
                    }
                ],
                "read_list": [
                    {
                        "id": self.book_3.id,
                        "title": "Казбек",
                        "book_slug": slugify("Казбек"),
                        "cover_url": f'http://testserver/media/{self.book_3.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_3.id,))}"
                    },
                    {
                        "id": self.book_4.id,
                        "title": "Аннапурна",
                        "book_slug": slugify("Аннапурна"),
                        "cover_url": f'http://testserver/media/{self.book_4.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_4.id,))}"
                    }
                ]
            },
            {
                "id": self.user_2.id,
                "username": "User",
                "first_name": "Kri",
                "last_name": "",
                "is_staff": False,
                "my_books": [
                    {
                        "id": self.book_3.id,
                        "title": "Казбек",
                        "book_slug": slugify("Казбек"),
                        "cover_url": f'http://testserver/media/{self.book_3.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_3.id,))}"
                    },
                    {
                        "id": self.book_4.id,
                        "title": "Аннапурна",
                        "book_slug": slugify("Аннапурна"),
                        "cover_url": f'http://testserver/media/{self.book_4.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_4.id,))}"
                    }
                ],
                "read_list": [
                    {
                        "id": self.book_1.id,
                        "title": "Еверест",
                        "book_slug": slugify("Еверест"),
                        "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
                    },
                    {
                        "id": self.book_2.id,
                        "title": "Ельбрус",
                        "book_slug": slugify("Ельбрус"),
                        "cover_url": f'http://testserver/media/{self.book_2.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_2.id,))}"
                    }
                ]
            }
        ]
        self.assertEqual(expected_data, data)

class ReviewSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.book_1 = BookG.objects.create(title='Book_1', content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Book_2', content='Content Book_2', pages=300)

        self.user_1 = User.objects.create(username='Fedya')
        self.user_2 = User.objects.create(username='Boris')

        self.review_1 = Review.objects.create(content='Norm Book_1', book=self.book_1, user=self.user_1, rating=4,
                                                                                                     is_anonymous=True)
        self.review_2 = Review.objects.create(content='Norm Book_2', book=self.book_2, user=self.user_2, rating=2)


    def test_ok_review_serializer(self):
        data = ReviewSerializer([self.review_1, self.review_2], many=True).data
        # ['id', 'content', 'book', 'user', 'rating', 'created_at', 'is_anonymous']
        expected_data = [
            {
                "id": self.review_1.id,
                "content": "Norm Book_1",
                "book": self.book_1.id,
                "user": self.user_1.id,
                "rating": 4,
                "created_at": today(),
                "is_anonymous": True
            },
            {
                "id": self.review_2.id,
                "content": "Norm Book_2",
                "book": self.book_2.id,
                "user": self.user_2.id,
                "rating": 2,
                "created_at": today(),
                "is_anonymous": False
            }
        ]

        self.assertEqual(expected_data, data)


class AuthorSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.author_1 = Author.objects.create(name='Дон Кихот', birthday='1835-12-25', biography='Don Kihot Biography')
        self.author_2 = Author.objects.create(name='Пушкин', birthday='1875-05-15', biography='Pushkin Biography')

        self.image_1, self.path_image_1 = create_test_image('image1.gpg')
        self.image_2, self.path_image_2 = create_test_image('image2.gpg')
        self.image_3, self.path_image_3 = create_test_image('image3.gpg')
        self.test_files = [self.path_image_1, self.path_image_2, self.path_image_3]

        self.book_1 = BookG.objects.create(title='Еверест', content='Content Book_1',
                                                                    cover=self.image_1, pages=200, author=self.author_1)
        self.book_2 = BookG.objects.create(title='Ельбрус', content='Content Book_2',
                                                                    cover=self.image_2, pages=300, author=self.author_1)
        self.book_3 = BookG.objects.create(title='Казбек', content='Content Book_3',
                                                                    cover=self.image_3, pages=400, author=self.author_2)

        self.base_url = 'http://testserver'

    def tearDown(self) -> None:
        tearDownFilesAndObjects([BookG], self.test_files)

    def test_ok_author_serializer(self):
        response = self.client.get(reverse('author-list'))
        context = {'request': response.wsgi_request}
        data = AuthorSerializer([self.author_1, self.author_2], context=context, many=True).data
        expected_data = [
            {
                "id": self.author_1.id,
                "name": "Дон Кихот",
                "author_slug": slugify("Дон Кихот"),
                "birthday": "1835-12-25",
                "biography": "Don Kihot Biography",
                "book_list": [
                    {
                        "id": self.book_1.id,
                        "title": "Еверест",
                        "book_slug": slugify("Еверест"),
                        "cover_url": f'http://testserver/media/{self.book_1.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_1.id,))}"
                    },
                    {
                        "id": self.book_2.id,
                        "title": "Ельбрус",
                        "book_slug": slugify("Ельбрус"),
                        "cover_url": f'http://testserver/media/{self.book_2.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_2.id,))}"
                    }
                ]
            },
            {
                "id": self.author_2.id,
                "name": "Пушкин",
                "author_slug": slugify("Пушкин"),
                "birthday": "1875-05-15",
                "biography": "Pushkin Biography",
                "book_list": [
                    {
                        "id": self.book_3.id,
                        "title": "Казбек",
                        "book_slug": slugify("Казбек"),
                        "cover_url": f'http://testserver/media/{self.book_3.cover.name}',
                        "book_url": f"{self.base_url}{reverse('bookg-detail', args=(self.book_3.id,))}"
                    }
                ]
            }
        ]
        # cons(expected_data)
        # cons(data)
        self.assertEqual(expected_data, data)


# class GenreSerializerTest(APITestCase):
#     def setUp(self):
#         self.genre = Genre.objects.create(name="Детектив")
#         self.book1 = BookG.objects.create(title="Испания не Куба", genre=self.genre)
#         self.book2 = BookG.objects.create(title="Sagrada Familia", genre=self.genre)
#
#     def test_genre_serializer(self):
#         url = reverse('genre-detail', args=[self.genre.id])  # Указываешь URL для жанра
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('book_list', response.data)  # Проверяем, что в ответе есть book_list
#         self.assertEqual(len(response.data['book_list']), 2)  # Проверяем количество книг в списке
#         self.assertIn('book_url', response.data['book_list'][0])  # Проверяем наличие ссылки на книгу