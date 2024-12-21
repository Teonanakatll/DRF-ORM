from django.db import models
from django.db.models import UniqueConstraint


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    age = models.PositiveSmallIntegerField(verbose_name='Возраст', null=True, blank=True)

    def __str__(self):
        return f'Имя автора {self.name}'

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name='Жанр')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class BookG(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE, verbose_name='Автор')
    pages = models.PositiveSmallIntegerField(verbose_name='Количество страниц', null=True, blank=True)
    genres = models.ManyToManyField(Genre, through='BookGenre', related_name='books', verbose_name='Жанры')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

class BookGenre(models.Model):
    book = models.ForeignKey(BookG, on_delete=models.CASCADE, verbose_name='Книга')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет жанра', default=1)

    def __str__(self):
        return f'{self.book.title} - {self.genre.name} (Приоритет: {self.priority}'

    class Meta:
        verbose_name = 'Связь книга жанр'
        verbose_name_plural = 'Связb книга жанр'
        constraints = [
            UniqueConstraint(fields=['book', 'genre'], name='unique_book_genre')
        ]

class Review(models.Model):
    content = models.TextField(verbose_name='Контент')
    book = models.ForeignKey(BookG, related_name='reviews', on_delete=models.CASCADE, verbose_name='Книга')
    rating = models.IntegerField(verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Дата создания')
    is_anonymous = models.BooleanField(default=False, verbose_name='Анонимно')

    def __str__(self):
        return f'Рецензия {self.content[:30]}'

    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
