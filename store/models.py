from django.contrib.auth.models import User
from django.db import models

from gpt4.utils import cons, conb


class Book(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена')
    author_name = models.CharField(max_length=255, verbose_name='Автор')

    # для обратного обращения от первичной модели User к Book дефолтное значение related_name='book_set
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')  # хозяин книг
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')        # читает книги
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True, verbose_name='Рейтинг')

    def __str__(self):
        return f'Id {self.id}: {self.name}'

    def get_info(self):
        print(f"Вот твоё инфо! Это книга {self.name}!")

    class Meta:
        ordering = ['id']

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
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, RATE {self.rate}'

    # Это определение конструктора класса UserBookRelation. Конструктор вызывается при создании нового экземпляра этого
    # класса. Внутри конструктора используются *args и **kwargs, которые позволяют передавать любое количество позиц.
    # и ключевых аргументов.
    #
    # super(UserBookRelation, self).__init__(*args, **kwargs)
    # Это вызов конструктора родительского класса. В Django модель UserBookRelation наследует от базового класса модели
    # models.Model. Этот вызов конструктора родителя (super()) позволяет инициализировать все поля и функциональность,
    # которые предоставляет Django для модели.
    #
    # super() вызывает метод родительского класса, чтобы правильно инициализировать объект на основе всех аргументов,
    # переданных в __init__.
    #
    # В __init__ вы можете инициализировать или изменять поля объекта, например, устанавливать значения по умолчанию или
    # выполнять предварительные вычисления.
    #
    # конструктор вызывается только при создании обьекта, один раз
    def __init__(self, *args, **kwargs):
        super(UserBookRelation, self).__init__(*args, **kwargs)
        self.old_rate = self.rate  # проверяем рейтинг до сохранения записи

    # функция которая вызывается при создании или обновлениии модели
    def save(self, *args, **kwargs):
        # избавляемся от кросс импорта
        from store.logic import set_rating

        # создаём флаг в который вернёт True если запись создаётся, и False если запись уже существует и просо обновл.
        creating = not self.pk

        # чтобы не сломать логику родительского метода save() и не перезаписать его, вызываем его и передаём аргументы
        super().save(*args, **kwargs)

        new_rate = self.rate  # проверяем рейтинг после сохранения записи
        cons(creating)
        conb('old_rating', self.old_rate)
        conb('new_rating', new_rate)
        cons('__________________________________________________')
        # вызываем нашу кастомную функцию установки рейтинга
        if self.old_rate != new_rate or creating:
            set_rating(self.book)
