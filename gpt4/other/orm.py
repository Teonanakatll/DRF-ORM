from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When, Value, Q, BooleanField, IntegerField, CharField, F, Avg, \
    FloatField, Max, Subquery, OuterRef
from django.db.models.functions import Concat

from gpt4.models import BookG, Author, Review, BookGenre, Genre

# pip install rich
# bold, italic, underline, strikethrough, reverse, blink, reset, color, on_color, link, spoiler, code, escaped, bold underline, bold italic, on_, bright_, black, red, green, yellow, blue, magenta, cyan, white, bright_
from rich.console import Console

from gpt4.utils import cons
from store.models import Book

console = Console()
console.print('second', style='yellow')

book = BookG.objects.get(id=1)
books = BookG.objects.all()
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
'bookennre__field'                 # когда обращаемся к полю промежуточной таблицы через её имя
BookG.objects.filter(bookgenres__rating__gt=4)
Genre.objects.annotate(sum_relation=Sum('bookgenre__rating'))

# при связи ManyToMany БЕЗ КАСТОМНОЙ таблицы:   по умолчанию прибавляю к полю связанной модели "__set" или
# согласно указанным related_name
# my_genres = ManyToManyField(Genre, related_name='my_books')
book.my_genres.all()
genre.my_books.all()
'my_genres__field'

for b in books:
    conb(b.title, b.pages)
    for r in b.reviews.all():
        cons(r.rating)

        #   ОСНОВНЫЕ ОПЕРАЦИИ С КВЕРИСЕТАМИ


# запрос происходит:    len(queryset),    list(queryset),    for obj in queryset,    print(queryset),   queryset[0]


books = BookG.objects.all()
print(books.query)  # выводим запрос в БД

# после применения values() продолжают работать методы filter(), exclude(), distinct(), order_by()
# annotate() и aggregate() только теперь работают с выбранными полями

# после применения values_list() остаются только значения полей модели без имён, работают только list(), len() и всё...

BookG.objects.all().values()                      # кверисет со списком словарей, с указанными в values полями, методы и поля модели перестанут работать

BookG.objects.all().values_list()                 # результат кверисет со списком кортежей с значениями полей модели

BookG.objects.values('name', 'price')     # выбор полей из модели

BookG.objects.all().values_list('id', flat=True)  # применяется только для одного поля, вернёт плоский список значений полей

BookG.objects.first()                             # вернёт первую запись

BookG.objects.last()                              # вернёт последнюю запись

BookG.objects.filter(id=3).exists()  # проверка существует ли запись, возвращает True/False

from django.forms.models import model_to_dict            # преобразует модель данных джанго в словарь

model = BookG.objects.first()
book_dict = model_to_dict(model)      # преобразует модель в словарь

# если нужно вывести список id связанных записей
book_dict['genres'] = [genre.id for genre in book.genres.all()]
book_dict['readers'] = [reader.id for reader in book.readers.all()]

book.refresh_from_db()     # обновляет атрибуты текущего экземпляра объекта модели данными из БД, если например запись
                            # была изменена на уровне запроса к БД или в другом экземпляре объекта

# получет или создаёт запись и вторым аргументом возвращает False если находит и True если создаёт
obj, created = BookGenre.objects.get_or_create(book=book, genre=genre)

# Это метод менеджера моделей Django, который пытается получить объект из базы данных с указанными параметрами (lookup).
# Параметр defaults используется для указания значений полей, которые нужно задать только при создании нового объекта
# Если объект уже СУЩЕСТВУЕТ, ОН НЕ БУДЕТ ОБНОВЛЁН, даже если переданы defaults.
obj, created = BookGenre.objects.get_or_create(defaults=None, **lookup)

from django.shortcuts import get_object_or_404
# получает запись или возвращает Http404 ошибку
BookG.objects.get_object_or_404(book=book, genre=genre)

# Позволяет найти объект по заданным условиям или создать его, если объект не найден. Если объект существует, он
# обновляется указанными значениями в defaults. ЕСЛИ ОБЬЕКТ НАЙДЕН ОН ОБЯЗАТЕЛЬНО ОБНОВЛЯЕТСЯ
obj, created = BookGenre.objects.update_or_create(book=book, genre=genre, defaults={"description": "Updated description"})

# Позволяют указать, какие поля загрузить из базы данных (или исключить). defer() и only(),а в случае обращения к
# исключённым полям просто будет дополнительный запрос к бд
BookG.objects.only('title', 'pages')
BookG.objects.defer('title', 'pages')


                                            # АНАЛИЗ ДАННЫХ И АГРЕГАЦИЯ

# Что делает: aggregate() используется для получения единственного итогового значения (например, суммы, среднего
# значения, минимального/максимального значения и т.д.) по всему набору данных. Это возвращает словарь с результатами
# агрегации, но не модифицирует отдельные записи, возвращает один словарь.
Book.objects.aggregate(average_rating=Avg('reviews__rating'))

# Агрегация возвращает примитивный float, который нельзя использовать с OuterRef или в Subquery.
# ТАК НЕ ПОЛУЧИТСЯ!!!!!! и смысла в первой аннотации нет так как вернётся только результат аггрегации
Author.objects.annotate(num_books=Count('books')).aggregate(average_rating=Avg('books__rating'))
# тут всё корректно, можно аггрегировать аннотированные значения
Author.objects.annotate(num_books=Count('books')).aggregate(average_rating=Avg('num_books'))

Book.objects.annotate(
    annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
    rating=Avg('userbookrelation__rate'),
    owner_name=Concat(F('owner__first_name'), Value(' '), F('owner__last_name'))  # Объединяем first_name и last_name
    ).select_related('owner').prefetch_related('readers').order_by('id')

# берётся поле 'product' (ForeignKey) для каждого уникального товара (каждого уникального product) добавляется новое
# поле total_price, которое будет содержать общую сумму стоимости всех заказов, в которых этот товар участвует
# аннотации будут группироваться по уникальным полям продукт, хотя мы и оталкиваемся от модели Order мы как уникальный
# id для аннотации можем выбрать уникальные id связанной модели
Order = ''
n = Order.objects.values('product').annotate(total_price=Sum(F('quantity') * F('product__price')))

n = [
    {'product': 2, 'total_price': 800},
    {'product': 3, 'total_price': 300}
    ]

# последовательное применение анотации и фильтрации по анотированному полю
BookG.objects.annotate(genre_count=Count('genres')).filter(genre_count__gt=2)
BookG.objects.filter(genres__name__icontains='Фантастика').annotate(revs=Count('reviews'))

# фильтрация в аггрегируемом поле
BookG.objects.annotate(count_reviews=Count('reviews', filter=Q(reviews__rating__lt=3))).order_by('-count_reviews')

# Итак, distinct() нужен, когда в запросе могут быть дубли для основной модели из-за фильтрации
# или агрегаций по связанным моделям.
Author.objects.filter(age__gte=33, books__pages__gt=130).distinct()    # выбор уникальных записей


                                            # ФИЛЬТРАЦИЯ И ОБНОВЛЕНИЕ ДАННЫХ

# __exact,   __iexact,   __contains,   __icontains,   __in (в списке),   __gt,   __gte,   __lt,   __lte,   __isnull
# __range (в диапазоне),   __startswith,   __istartswith,   __endswith,   __iendswith,   __year,   __month,   __day

# проверка заполнения поля кроме поля ManyToMany/ForKey только на None, на 0/""/False использ. разные проверки
BookG.objects.filter(field=None)

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

# происходит создание промежуточных записей в результирующем запросе. Это связано с тем, что джойны таблиц (books и
# reviews) порождают дублирование строк, если у книги несколько отзывов (reviews). дубли возникают вероятно изза
# двух джоинов к модели books для подсчета рейтинго и доновременно для подсчёта самой books
Author.objects.annotate(avg_rate=Avg('books__reviews__rating'), count_books=Count('books', distinct=True))


# условия When работают аналогично фильтрам в filter(): __gt,   __lt,   __exact, __in...,  Q() классы и ид
# добавляем then поле которое в зависимости от значения другого поля добавляет в аннотируемое разные значения
# Value() / output_field когда нужно задать тип str, int, bool, data, простые счётчики пишем просто then=1
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

# допустимо устанавливать простые значения без указания Value() / output_field: then=1
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


# Класс F в Django используется для ссылок на поля модели в запросах, позволяя работать с полями без извлечения их
# значений в Python. Он позволяет оперировать с полями непосредственно на уровне базы данных, например, при обновлениях
# или аннотациях. Это дает возможность выполнять операции над полями в SQL запросах, не вытягивая их в память.
# чтобы выполнить арифметические операции или сравнения

Book.objects.annotate(price_increased=F('price') * 1.1)  # Увеличиваем цену на 10%

Book.objects.filter(id=1).update(price=F('price') + 10)  # Увеличиваем цену на 10

Book.objects.filter(price__gt=F('discount_price'))  # Книги, у которых цена больше скидочной

# порядок вызова метод. (annotate, select_related, prefetch_related) в цепочке Django ORM запроса не влияет на результат
Book.objects.annotate(annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                                     rating=Avg('userbookrelation__rate'),
                                     owner_name=F('owner__name'))\
                                     .select_related('owner').prefetch_related('readers').order_by('id')

# Класс Q используется для создания сложных фильтров и условий запросов, когда необходимо объединить несколько фильтров
# с логическими операторами, такими как AND, OR, а также для более сложной логики, например, при использовании отрицаний
# (NOT), в методах filter() или exclude()
# И - &,    ИЛИ - |,    НЕ - ~Q()

# исключение записей по фильтру
Book.objects.exclude(Q(author='John') | Q(pages__lt=100))

Author.objects.annotate(
    valid_books=Count('books', filter=Q(books__title__icontains='Куба') & Q(books__pages=50)),
    books_count=Count('books')
    ).filter(valid_books=F('books_count'))


Author.objects.annotate(
    valid_books=Count('books', filter=Q(books__title__icontains='Куба') & Q(books__pages=50)),
    total_books=Count('books')
    ).filter(valid_books__gte=F('total_books') / 2)


                                                #  РАБОТА СО ВРЕМЕНЕМ И ДАННЫМИ

# удаление записей старше одного месяца
from django.utils import timezone
# pip install python-dateutil
from dateutil.relativedelta import relativedelta  # позволяет указывать месяцы и годы
one_month_ago = timezone.now() - relativedelta(months=1)
# работа с полем DateTimeField()  удаление записей старше одного месяца - тоесть меньше чем указанная дата
Review.objects.filter(is_anonymous=True, created_at__lt=one_month_ago).delete()


time = timezone.now() - relativedelta(years=5)
# Преобразуем в дату (без времени)
target_date = time.date()
# фильтрация по полю DateField()  (без времени)
Author.objects.filter(birth_date__gt=target_date)


# преобразование строки в формат datetime для заполнения поля DateField()
from datetime import datetime
dates_list = ['1981-07-05', '1835-12-25', '1345-01-30']

# strptime() — это метод в модуле datetime, который используется для преобразования строки в объект datetime с помощью
# заданного формата, формат %Y-%m-%d, что значит, что строка имеет вид "Год-Месяц-День"
dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates_list]


# enumerate() — это встроенная функция Python, которая используется для получения индекса и элемента при итерации по
# итерируемому объекту, например, по списку или строке.
for i, author in enumerate(Author.objects.all()):
    author.birthday = dates[i]
    author.save()

# DateTimeField вы можете использовать такие фильтры, как year, month, day, hour, minute, second


# Если нужна простая оценка по годам без учёта месяцев и дней, используй ExtractYear
from django.db.models.functions import ExtractYear
# понял тоесть если это поле модели могу смело использовать F('birthday__year') так понятнее а
# когда уже столкнусь не с полями вспомню что существует способ экстракции откуда угодно?)
# Для простого фильтра или обращения к году в QuerySet или модели, удобнее F('birthday__year').

current_year = timezone.now().year
authors = Author.objects.annotate(age=current_year - ExtractYear('birthday')).filter(age__gt=30)

Author.objects.annotate(
    age=(ExtractYear(timezone.now()) - ExtractYear(F('birthday')))).filter(age__gt=30)

# Если важна точность до месяца и дня, используй второй вариант с ExpressionWrapper
from django.db.models import F, ExpressionWrapper, fields
from django.utils import timezone

date_now = timezone.now()
authors = Author.objects.annotate(
    age=ExpressionWrapper(
        (date_now.year - F('birthday__year')) -
        ((date_now.month, date_now.day) < (F('birthday__month'), F('birthday__day'))),
        output_field=fields.IntegerField()
    )
)

# Выведи жанры, которые связаны с книгами, где хотя бы 30% отзывов имеют рейтинг ниже 2.
# умножаем одно из чиселовых значений на 0.1 чтобы получить десятичную дробь чтобы гарантировать точный рез. деления
# а иначе в бд результатам деления целых чисел будет целое число
from django.db.models.functions import Round
genres = Genre.objects.annotate(count_books=Count('books'), reviews_abow_two=Count('books', filter=Q(books__reviews__rating__lt=2)),
                                percent=ExpressionWrapper(F('reviews_abow_two') * 1.0 / F('count_books') * 100,
                              output_field=FloatField())).annotate(round_precent=Round('percent', 2)).filter(round_precent__gt=30)




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
book.author = None  # Удаляет связь в ForeignKey, можно только разорвать прямую связь
book.save()

# Обратная связь ForeignKey
author.book_set.create(title='Che', pages=100)      # create() для создания и автоматической привязки

# ManyToMany С КАСТОМНОЙ промежуточной таблицей,    # create()
# my_genres = ManyToManyField(Genre, through='BookGenres', related_name='my_books')
# промежуточной таблицы и передать ей оба экземпляра класса которые необходимо связать
relation = BookGenre.objects.create(book=book, author=author)

# ManyToMany БЕЗ КАСТОМНОЙ промежуточной таблицы. Используем add()
# my_genres = ManyToManyField(Genre, related_name='my_books')
book.my_genres.add(genre)                   # этот вариант предпочтительней
book.my_genres.add(genre.id)
book.my_genres.add(genre1, genre2)
book.my_genres.add(*[genre1, genre2])

# полностью ПЕРЗАПИСЫВАЕТ связанные записи, если передать пустой список\кортеж то связи очистятся
book.my_genres.set(genre1, genre2)

book.my_genres.remove(genre)  # Удаляет жанр из книги
genre.my_books.remove(book)  # Удаляет книгу из жанра

                                                    # Subquery
# Subquery возвращает значения, которые можно использовать:
# Для аннотации (annotate) — добавления вычисленных полей к объектам.
# Для фильтрации (filter) — применения условий к объектам.
# Однако, результатом Subquery всегда будет одно значение на строку результата основного запроса, которое
# присваивается объекту. Если Subquery возвращает более одного значения (например, список), это вызовет ошибку.

# 1. Аннотация: максимальный рейтинг книги для каждого жанра
Genre.objects.annotate(top_book_rating=Subquery(Book.objects.filter(genres=OuterRef('pk'))
                                             .values('genres').annotate(max_rating=Max('reviews__rating'))
                                             .values('max_rating')[:1]))

# 2. Фильтрация: жанры с максимальным рейтингом книги выше 4
Genre.objects.annotate(max_rating=Subquery(BookG.objects.filter(genres=OuterRef('pk'))
                                           .values('genres').annotate(max_rating=Max('reviews__rating'))
                                           .values('max_rating')[:1])).filter(max_rating__gt=4)


# 3. Аннотация: средний рейтинг книг для каждого автора
authors = Author.objects.annotate(avg_book_rating=Subquery(BookG.objects.filter(author=OuterRef('pk'))
                                               .values('author').annotate(avg_rating=Avg('reviews__rating'))
                                               .values('avg_rating')[:1]))
# что по сути равно -
Author.objects.annotate(avg_book_rating=Avg('books__reviews__rating'))

Department, Employee, Order = 0, 0, 0
# рассчитать среднюю зарплату для каждого отдела, но только по работникам, чей возраст превышает определённый порог.
Department.objects.annotate(
    avg_salary_above_30=Subquery(
        Employee.objects.filter(department=OuterRef('pk'), age__gt=30)
        .values('department')
        .annotate(avg_salary=Avg('salary'))
        .values('avg_salary')[:1]
    )
)    # тоесть тут через строчную анотацию мы можем добраться только ко всем Employee и можем только посчитать для всех
     # а через subquery мы можем сузить выборку только для необходимых обьектов отфильтровав и аггр. только их значения

# анотируем книги максимальным рейтингом автора.
Book.objects.annotate(
    max_rating_by_author=Subquery(
        Book.objects.filter(author=OuterRef('author'))
        .values('author')
        .annotate(max_rating=Max('reviews__rating'))
        .values('max_rating')[:1]
    )
)  # тут если пробовать обращаться с помощю стр. аннотации получится рекурсия 'author__books__reviews__rating'?

# получаем пользователей, у которых средний рейтинг книг выше некоторого порога, используя подзапрос для вычис среднего.
User.objects.annotate(
    avg_rating=Subquery(
        Book.objects.filter(owner=OuterRef('pk'))
        .annotate(avg_book_rating=Avg('reviews__rating'))
        .values('avg_book_rating')[:1]
    )
).filter(avg_rating__gt=4.0)
# а тут кажется можно и без подзапроса User.objects.annotate(avg_rating=Avg('reviews__rating').filter(avg_rating__gt=4.0)

# выбери заказы, которые имеют максимальную стоимость среди всех заказов одного пользователя.
Order.objects.annotate(
    max_order_price=Subquery(
        Order.objects.filter(user=OuterRef('user'))
        .values('user')
        .annotate(max_price=Max('total_price'))
        .values('max_price')[:1]
    )
).filter(total_price=F('max_order_price'))
# тут по видемому тоже получится рекурсия если обращаться черес стр анотацию Max('user__orders__total-price')?

from django.db.models.functions import Coalesce

# Заменяем NULL на 0 и выполняем вычисления
books = Book.objects.annotate(
    adjusted_rate=Coalesce('rate', Value(0))  # Заменяем NULL на 0
).annotate(
    result=F('adjusted_rate') * 2  # Выполняем вычисления безопасно
)

