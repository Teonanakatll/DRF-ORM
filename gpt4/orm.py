from django.db.models import Sum, Count, Case, When, Value, Q, BooleanField, IntegerField, CharField, F
from gpt4.models import BookG, Author, Review, BookGenre, Genre

# pip install rich
# bold, italic, underline, strikethrough, reverse, blink, reset, color, on_color, link, spoiler, code, escaped, bold underline, bold italic, on_, bright_, black, red, green, yellow, blue, magenta, cyan, white, bright_
from rich.console import Console

console = Console()
console.print('second', style='yellow')

book = BookG.objects.get(id=1)
genre = Genre.objects.get(id=1)
author = Author.objects.get(id=1)

                                                # ОБРАЩЕНИЕ К ПОЛЯМ СВЯЗАННЫХ МОДЕЛЕЙ
# прямая связь ForeignKey
book.author
book.author.name

# обратная связь ForeignKey
author.books_set.all()    # или через related_name имя обратной связи указанной в book
author.my_books.all()

# связь ManyToMany С КАСТОМНОЙ промежуточной таблицей:
# my_genres = ManyToManyField(Genre, through='BookGenres', related_name='my_books')
book.my_genres.all()
genre.my_books.all()
'my_books__field'
# обращение к промежуточной таблице и из неё согласно правилам и синтаксису связи ForeignKey и наличию related_name
book.bookgenre_set.all()
genre.bookgenre_set.all()
BookG.objects.filter(bookgenres__rating__gt=4)
Genre.objects.annotate(sum_relation=Sum('bookgenres__rate'))

# при связи ManyToMany БЕЗ КАСТОМНОЙ таблицы:   по умолчанию прибавляю к полю связанной модели "s" или
# согласно указанным related_name
book.genres.all()
genre.books.all()
'books__field'






                                                 #   ОСНОВНЫЕ ОПЕРАЦИИ С КВЕРИСЕТАМИ


# запрос происходит:    len(queryset),    list(queryset),    for obj in queryset,    print(queryset),   queryset[0]


books = BookG.objects.all()
print(books.query)  # выводим запрос в БД

BookG.objects.all().values()                      # кверисет со списком словарей, с указанными в values полями, методы и поля модели перестанут работать

BookG.objects.all().values_list()                 # результат кверисет со списком кортежей с значениями полей модели

BookG.objects.values('name', 'price')     # выбор полей из модели

BookG.objects.all().values_list('id', flat=True)  # применяется только для одного поля, вернёт плоский список значений полей

BookG.objects.first()                             # вернёт первую запись

BookG.objects.last()                              # вернёт последнюю запись

BookG.objects.filter(id=3).exists()  # проверка существует ли запись, возвращает True/False

from django.forms import model_to_dict            # преобразует модель данных джанго в словарь

model = BookG.objects.first()
model_to_dict(model)                              # преобразует модель в словарь

BookG.refresh_from_db()     # обновляет атрибуты текущего экземпляра объекта модели данными из БД, если например запись была изменена на уровне запроса к БД или в другом экземпляре объекта



                                            # АНАЛИЗ ДАННЫХ И АГРЕГАЦИЯ

# берётся поле 'product' (ForeignKey) для каждого уникального товара (каждого уникального product) добавляется новое поле total_price, которое будет содержать общую сумму стоимости всех заказов, в которых этот товар участвует
n = BookG.objects.values('product').annotate(total_price=Sum('quantity' * 'product__price'))

n = [{'product': 2, 'total_price': 800}, {'product': 3, 'total_price': 300}]

# последовательное применение анотации и фильтрации по анотированному полю
BookG.objects.annotate(genre_count=Count('genres')).filter(genre_count__gt=2)
BookG.objects.filter(genres__name__icontains='Фантастика').annotate(revs=Count('reviews'))

# фильтрация в аггрегируемом поле
BookG.objects.annotate(count_reviews=Count('reviews', filter=Q(reviews__rating__lt=3))).order_by('-count_reviews')


Author.objects.filter(age__gte=33, books__pages__gt=130).distinct()    # выбор уникальных записей


                                            # ФИЛЬТРАЦИЯ И ОБНОВЛЕНИЕ ДАННЫХ

BookG.objects.filter(field=None)                                # проверка заполнения поля кроме поля ManyToMany/ForKey

BookG.objects.filter(genres__isnull=True)                       # проверка заполнения поля ManyToMany/ForeignKey

BookG.objects.filter(author__isnull=False)                      # проверка, что связь с ForeignKey или ManyToMany не пуста

Author.objects.filter(bookg_set__isnull=True)                   # проверка, что записи не связаны с книгами, обратная свзь

BookG.objects.filter(author="Сява").update(status="published")  # обновляем данные напрямую в БД

# напрямую в обратной ForeignKey и в ManyToMany я могу проверить на равенство только id, чтобы сравнить с количеством необходимо применить аннотацию
Author.objects.filter(Q(books__title__icontains='Путешествие') & Q(books=1))
Author.objects.annotate(all_books=Count('books')).filter(Q(all_books=1) & Q(books__title__icontains='Путешествие'))



# анотируем поле подсчитанными полями отфильтрованными с помощью условия, сортируем по этому полю и берём первое
Author.objects.annotate(books_above_4=Count('books__reviews',
                                            filter=Q(books__reviews__rating__gt=4))).order_by('-books_above_4').first()

# условия When работают аналогично фильтрам в filter(): __gt,   __lt,   __exact, __in...,  Q() классы и ид
# добавляем анотированное поле которое в зависимости от значения другого поля добавляет в аннотируемое разные значения
BookG.objects.annotate(
    is_special=Case(
        When(field1='value1', then=Value(True)),
        default=Value(False),
        output_field=BooleanField()  # при аннотации указывать тип возврвщаемых данных
    )
)


# логика для множественного обновления с условиями (аналог if/else)
BookG.objects.update(
    status=Case(
        When(author="Сява", then=Value("published")),
        When(author="Иван", then=Value("draft")),
        default=Value("archived")                         # значение по умолчанию
    )
)

BookG.objects.update(
    some_field=Case(
        When(other_field='value', then=Value(1)),
        default=Value(0),
        output_field=IntegerField()
    )
)

BookG.objects.annotate(
    tag=Case(
        When(Q(pages__gte=1000) & Q(status='published'), then=Value('Popular')),
        When(Q(pages__lt=100) | Q(status='draft'), then=Value('Ignored')),
        default=Value('Normal'),
        output_field=CharField()
    )
)

                                                # КЛАСС F, Q

# И - &,    ИЛИ - |,    НЕ - ~Q(),  НЕ РАВНО - <>,  и все остальные  = >= > < <=

Author.objects.annotate(
    valid_books=Count('books', filter=Q(books__title__icontains='Куба') & Q(books__pages=50)),
    books_count=Count('books')).filter(valid_books=F('books_count'))


Author.objects.annotate(
    valid_books=Count('books', filter=Q(books__title__icontains='Куба') & Q(books__pages=50)),
    total_books=Count('books')
).filter(valid_books__gte=F('total_books') / 2)


                                                #  РАБОТА СО ВРЕМЕНЕМ И ДАННЫМИ

# удаление записей старше одного месяца
from django.utils import timezone
from datetime import timedelta
one_month_ago = timezone.now() - timedelta(days=30)
Review.objects.filter(is_anonymous=True, created_at__lt=one_month_ago).delete()  # удаление записей за месяц


                                                      # СОЗДАНИЕ СВЯЗЕЙ С МОДЕЛЯМИ
author = Author.objects.last()
book = BookG.objects.first()
genre = Genre.objects.get(id=1)

# Прямая связь ForeignKet
book.author = author            # наппямую присваиваем экземпляр первичной модели, данные веншнего ключа author_id меняются автоматически
book.author_id = author.id      # это внешний ключ, который хранит только ID записи в таблице Author
book.save()
BookG.objects.create(author=author, title='Che')

# Важно, что внешний ключ может быть настроен на null=True, чтобы позволить присваивание None. Если null=False,
# Django не позволит сохранить значение None в поле.
book.author = None  # Удаляет связь, в ForeignKey с любой стороны можно только разорвать прямую связь

# Обратная связь ForeignKey
author.book_set.create(title='Che', pages=100)      # create() для создания и автоматической привязки

# ManyToMany С КАСТОМНОЙ промежуточной таблицей,    # create()
# промежуточной таблицы и передать ей оба экземпляра класса которые необходимо связать
relation = BookGenre.objects.create(book=book, author=author)

# ManyToMany БЕЗ КАСТОМНОЙ промежуточной таблицы. Используем add()
book.genres.add(genre)                   # этот вариант предпочтительней
book.genres.add(genre.id)
book.genres.add(genre1, genre2)
book.genres.add(*[genre1, genre2])

book.genres.remove(genre)  # Удаляет жанр из книги
genre.books.remove(book)  # Удаляет книгу из жанра