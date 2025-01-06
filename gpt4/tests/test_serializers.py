from django.contrib.auth.models import User
from django.test import TestCase
from datetime import datetime

from django.utils import timezone


from gpt4.models import Author, BookG, Genre, UserBookGRelation
from gpt4.serializers import BookGSerializer
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
                "title": self.book_1.title,
                "content": self.book_1.content,
                "author": self.author_1.id,
                "owner": self.user_1.id,
                "pages": self.book_1.pages,
                "avg_hate_rate": '3.50',
                "view_created_at": self.today,
                "genres": [
                    {
                        "id": self.genre_1.id,
                        "name": self.genre_1.name
                    },
                    {
                        "id": self.genre_2.id,
                        "name": self.genre_2.name
                    }
                ]
            },
            {
                "id": self.book_2.id,
                "title": self.book_2.title,
                "content": self.book_2.content,
                "author": self.author_2.id,
                "owner": self.user_2.id,
                "pages": self.book_2.pages,
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