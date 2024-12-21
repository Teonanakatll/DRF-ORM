from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.test import TestCase

from gpt4.utils import cons
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')

        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 2', owner=user2)

        UserBookRelation.objects.create(user=user1, book=book_1, like=True)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True)

        # важно для теста сериалзатора, если убрать из фильтра сериализатора like=True она сломает тест (покажет)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        # data = Book.objects.annotate(annotated_likes=Count('userbookrelation', filter=Q(userbookrelation__like=True))).order_by('id')

        data = Book.objects.annotate(annotated_likes=Count('readers__userbookrelations__like', filter=Q(readers__userbookrelation__like=True))).order_by('id')

        cons(data.query)



        data = BooksSerializer(data, many=True).data
        cons(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'owner': user1.id,
                'likes_count': 3,
                'annotated_likes': 3
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'owner': user2.id,
                'likes_count': 2,
                'annotated_likes': 2
            },
        ]
        self.assertEqual(expected_data, data)