from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint

# Когда ты смотришь на модель или поле, полезно задавать себе такие вопросы:
#
# Обязательно ли это поле для формы? (Использовать blank=False или blank=True)
# Может ли это поле быть пустым в базе данных? (Использовать null=True или null=False)
# Должно ли поле иметь значение по умолчанию? (Использовать default=<значение>)
# Должно ли поле быть уникальным? (Использовать unique=True)
# Поле часто используется в запросах? (Использовать db_index=True)
# Поле является внешним ключом? (Использовать related_name, related_query_name)
# Поле имеет ограниченный набор значений? (Использовать choices)
from gpt4.utils import cons

# from django.utils.text import slugify
# def save(self, *args, **kwargs):
#     if not self.slug:
#         self.slug = slugify(self.title)
#     super().save(*args, **kwargs)


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    # Обычно для строковых полей рекомендуется использовать blank=True вместо null=True, так как в Django строковые
    # поля, как правило, хранят пустую строку, а не NULL, чтобы избежать путаницы.
    # blank управляет валидацией в форме, а null - тем, как значения хранятся в базе данных.
    birthday = models.DateField(blank=True, null=True, verbose_name='Год рождения')
    biography = models.TextField(blank=True, verbose_name='Биография')

    def __str__(self):
        return f'Имя автора {self.name}'

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    pw = models.CharField(max_length=30, blank=True, verbose_name='Пароль')

class Genre(models.Model):
    name = models.CharField(max_length=50, verbose_name='Жанр')
    description = models.TextField(verbose_name='Описание', blank=True, default='Нет описания')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class BookG(models.Model):
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    author = models.ForeignKey(Author, related_name='books', null=True, on_delete=models.SET_NULL, verbose_name='Автор')
    pages = models.PositiveSmallIntegerField(verbose_name='Количество страниц')
    genres = models.ManyToManyField(Genre, through='BookGenre', related_name='books', verbose_name='Жанры')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Дата добавления')
    # кеширующее поле
    avg_hate_rate = models.DecimalField(default=0, max_digits=3, decimal_places=2, verbose_name='Средний рейтинг')
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='owner_books', verbose_name='Хозяин')
    readers = models.ManyToManyField(User, through='UserBookGRelation', related_name='readers_books', verbose_name='Читатели')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ('id',)

class BookGenre(models.Model):
    book = models.ForeignKey(BookG, on_delete=models.CASCADE, verbose_name='Книга')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name='Жанр')
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет жанра', default=1)

    def __str__(self):
        cons(f'{self.book.title} - {self.genre.name} (Приоритет: {self.priority})')
        return f'{self.book.title} - {self.genre.name} (Приоритет: {self.priority})'

    class Meta:
        verbose_name = 'Связь книга жанр'
        verbose_name_plural = 'Связb книга жанр'
        constraints = [
            UniqueConstraint(fields=['book', 'genre'], name='unique_book_genre')
        ]

class UserBookGRelation(models.Model):
    HATE_CHOICES = [
        (0, 'None'),
        (1, 'Mud'),
        (2, 'Trash'),
        (3, 'Shit'),
        (4, 'Garbage'),
        (5, 'Toxic')
    ]

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    book = models.ForeignKey(BookG, on_delete=models.CASCADE)

    like = models.BooleanField(default=False, verbose_name='Лайк')
    in_bookmarks = models.BooleanField(default=False, verbose_name='В закладках')
    hate_rate = models.PositiveSmallIntegerField(default=0, choices=HATE_CHOICES, verbose_name='Рейтинг ненависти')

    def __str__(self):
        return f'{self.user.username}, {self.book.title} - HATE RATE: {self.hate_rate}'

    class Meta:
        verbose_name = 'Связь юзер книга'
        verbose_name_plural = 'Связи юзер книга'
        constraints = [
            UniqueConstraint(fields=['user', 'book'], name='unique_user_book')
        ]

    def clean(self):
        valid_choices = [choice[0] for choice in self.HATE_CHOICES]
        if self.hate_rate not in valid_choices:
            raise ValidationError(f'Invalid hate_rate. Choice a valid value from {", ".join(map(str, valid_choices))}, your :{self.hate_rate}')
        super().clean()

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
        super(UserBookGRelation, self).__init__(*args, **kwargs)
        self.old_rate = self.hate_rate  # устанавливаем рейтинг до сохранения записи

    # функция которая вызывается при создании или обновлениии модели
    def save(self, *args, **kwargs):
        # избавляемся от кросс импорта
        from gpt4.utils_drf import set_avg_hate_rate

        # создаём флаг в который вернёт True если запись создаётся, и False если запись уже существует и просо обновл.
        creating = not self.pk

        # Метод clean() автоматически не вызывается при прямом вызове .save() (если ты не вызываешь его вручную), но
        # будет вызван при валидации формы или сериализатора. Поэтому, чтобы везде работала проверка, лучше
        # явно прописывать вызов self.clean() в методе save() модели.
        self.clean()             # проверяем что значение не выходит за пределы чойсов

        # чтобы не сломать логику родительского метода save() и не перезаписать его, вызываем его и передаём аргументы
        super().save(*args, **kwargs)

        new_rate = self.hate_rate  # проверяем рейтинг после сохранения записи
        # вызываем нашу кастомную функцию установки рейтинга
        if self.old_rate != new_rate or creating:
            set_avg_hate_rate(self.book)

        # Обновляем значение self.old_rate, чтобы оно всегда соответствовало текущему значению hate_rate
        self.old_rate = self.hate_rate  # для того, чтобы при следующем обновлении сравнивать правильные значения


class Review(models.Model):
    RATING = [(i, i) for i in range(11)]

    content = models.TextField(verbose_name='Контент')
    book = models.ForeignKey(BookG, related_name='reviews', on_delete=models.CASCADE, verbose_name='Книга')
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.SET_NULL, null=True, verbose_name='Пользов')
    rating = models.IntegerField(verbose_name='Рейтинг', choices=RATING)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Дата создания')
    is_anonymous = models.BooleanField(default=False, verbose_name='Анонимно')

    def __str__(self):
        return f'Рецензия {self.content[:30]}'

    # проверяем что передаваемое значение не выходит за пределы чойсов
    # def clean(self):
    #     if self.rating not in dict(self.RATING).keys():
    #         raise ValidationError(f'Invalid rating. Choose a valid value from {dict(self.RATING).keys()}')
    #     super().clean()
    #
    # def save(self, *args, **kwargs):
    #     self.clean()          # вызываем метод перед сохранением
    #     super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
        constraints = [
            UniqueConstraint(fields=['user', 'book'], name='unique_constrain_review')
        ]

    # валидация чойса
    def clean(self):
        valid_choices = [choice[0] for choice in self.RATING]
        if self.rating not in valid_choices:
            raise ValidationError(f'Invalid hate_rate. Choice a valid value from {", ".join(map(str, valid_choices))}, your :{self.rating}')
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        # чтобы не сломать логику родительского метода save() и не перезаписать его, вызываем его и передаём аргументы
        super().save(*args, **kwargs)
