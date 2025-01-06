from django.contrib.auth.models import User
from django.db.models import Count, Q, Case, When, Avg, F
from django.test import TestCase

from gpt4.utils import cons
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksSerializerTestCase(TestCase):
    # в тестах сериализатора тестируется правильность валидации входных данных и
    # Корректность преобразования данных модели в JSON (и наоборот).
    def test_ok(self):
        user1 = User.objects.create(username='user1', first_name='Ivan', last_name='Petrov')
        user2 = User.objects.create(username='user2', first_name='Ivan', last_name='Sidorov')
        user3 = User.objects.create(username='user3', first_name='1', last_name='2')

        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author 2', owner=user2)

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)

        # отдельно проверяем изменение рейтинго, так как при простом добовлении обьекта userbookrelation срабатывает
        # условие created, и чтобы нам проверить условие при изменении моделей надо это изменение организовать
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)

        # важно для теста сериалзатора, если убрать из фильтра сериализатора like=True она сломает тест (покажет)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        # data = Book.objects.annotate(annotated_likes=Count('userbookrelation', filter=Q(userbookrelation__like=True))).order_by('id')


        data = Book.objects.annotate(annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                     owner_name=F('owner__username')) \
                                     .select_related('owner').prefetch_related('readers').order_by('id')


        # cons(data.query)



        data = BooksSerializer(data, many=True).data
        # cons(data)
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Author 1',
                'owner_name': user1.username,
                'annotated_likes': 3,
                'rating': '4.67',
                'readers_abc': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Author 2',
                'owner_name': user2.username,
                'annotated_likes': 2,
                'rating': '3.50',
                'readers_abc': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Sidorov'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    }
                ]
            },
        ]
        # cons(data)
        # cons(expected_data)
        self.assertEqual(expected_data, data)

    def tearDown(self) -> None:
        User.objects.all().delete()
        Book.objects.all().delete()
        UserBookRelation.objects.all().delete()
        super().tearDown()
