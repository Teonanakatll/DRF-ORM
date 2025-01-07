from django.contrib.auth.models import User
from django.test import TestCase
from datetime import datetime

from django.utils import timezone


from gpt4.models import Author, BookG, Genre, UserBookGRelation
from gpt4.serializers import BookGSerializer, UserBookGRelationSerializer, UserSerializer
from gpt4.utils import cons


class BookGSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.today_string = str(timezone.now().date())
        self.today = datetime.strptime(self.today_string, '%Y-%m-%d').date()

        self.author_1 = Author.objects.create(name='Teon')
        self.author_2 = Author.objects.create(name='Kreon')

        self.user_1 = User.objects.create(username='Fedya')
        self.user_2 = User.objects.create(username='Boris')

        self.genre_1 = Genre.objects.create(name='Thriller')
        self.genre_2 = Genre.objects.create(name='Comedy')

        self.book_1 = BookG.objects.create(title='Everest', author=self.author_1,
                                           owner=self.user_1, pages=300, content='content1')
        self.book_1.genres.set([self.genre_1, self.genre_2])
        self.book_2 = BookG.objects.create(title='Elbrus', author=self.author_2,
                                           owner=self.user_2, pages=250, content='content2')

        self.relation_1 = UserBookGRelation.objects.create(book=self.book_1, user=self.user_1, hate_rate=5)
        self.relation_2 = UserBookGRelation.objects.create(book=self.book_1, user=self.user_2, hate_rate=2)
        self.relation_3 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_1)
        self.relation_4 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_2, hate_rate=5)

    def test_ok(self):

        books = BookG.objects.all()
        data = BookGSerializer(books, many=True).data
        # cons(data)

        expected_data = [
            {
                "id": self.book_1.id,
                "title": "Everest",
                "content": "content1",
                "author": self.author_1.id,
                "owner": self.user_1.id,
                "pages": 300,
                "avg_hate_rate": '3.50',
                "view_created_at": self.today,
                "genres": [
                    {
                        "id": self.genre_1.id,
                        "name": "Thriller"
                    },
                    {
                        "id": self.genre_2.id,
                        "name": "Comedy"
                    }
                ]
            },
            {
                "id": self.book_2.id,
                "title": "Elbrus",
                "content": "content2",
                "author": self.author_2.id,
                "owner": self.user_2.id,
                "pages": 250,
                "avg_hate_rate": '2.50',
                "view_created_at": self.today,
                "genres": []
            }
        ]
        # cons(data)
        # cons(expected_data)
        self.assertEqual(expected_data, data)


    def tearDown(self) -> None:
        User.objects.all().delete()
        Author.objects.all().delete()
        BookG.objects.all().delete()
        Genre.objects.all().delete()
        UserBookGRelation.objects.all().delete()
        super().tearDown()

class UserBookGRelationSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Teon', is_staff=True)

        self.book_1 = BookG.objects.create(title='Book_1', content='Content Book_1', pages=200)
        self.book_2 = BookG.objects.create(title='Book_2', content='Content Book_2', pages=300)

        self.relation_1 = UserBookGRelation.objects.create(book=self.book_1, like=True, in_bookmarks=True, hate_rate=3)
        self.relation_2 = UserBookGRelation.objects.create(book=self.book_2, user=self.user_1, hate_rate=5)

    def test_ok(self):
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

    def tearDown(self) -> None:
        User.objects.all().delete()
        BookG.objects.all().delete()
        UserBookGRelation.objects.all().delete()
        super().tearDown()

class UserSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='Boss', first_name='Teon', last_name='Ko', is_staff=True)
        self.user_2 = User.objects.create(username='User', first_name='Kri')

    def test_ok(self):
        users = User.objects.all()
        data = UserSerializer(users, many=True).data

        expected_data = [
            {
                "id": self.user_1.id,
                "username": "Boss",
                "first_name": "Teon",
                "last_name": "Ko",
                "is_staff": True
            },
            {
                "id": self.user_2.id,
                "username": "User",
                "first_name": "Kri",
                "last_name": "",
                "is_staff": False
            }
        ]
        self.assertEqual(expected_data, data)

    def tearDown(self) -> None:
        User.objects.all().delete()
        super().tearDown()