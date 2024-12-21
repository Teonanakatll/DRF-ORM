from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена')
    author_name = models.CharField(max_length=255, verbose_name='Автор')

    # для обратного обращения от первичной модели User к Book дефолтное значение related_name='book_set
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')  # хозяин книг
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')        # читает книги

    def __str__(self):
        return f'Id {self.id}: {self.name}'

    def get_info(self):
        print(f"Вот твоё инфо! Это книга {self.name}!")


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    like = models.BooleanField(default=False, verbose_name='Лайк')
    in_bookmarks = models.BooleanField(default=False, verbose_name='В закладках')
    rate = models.PositiveSmallIntegerField(null=True, choices=RATE_CHOICES, verbose_name='Рейтинг')
    comment = models.TextField(null=True, verbose_name='Комментарий')

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, RATE {self.rate}'

