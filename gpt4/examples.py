from django.utils import timezone
from datetime import timedelta

from django.db.models import Count, Avg, Q, Case, When, Value, Max, CharField, Sum, F, ExpressionWrapper, IntegerField, \
    FloatField, Min

from gpt4.models import BookG, Author, Review, Genre

BookG.objects.filter(title__icontains='Куба').order_by('title')

Author.objects.values('name').annotate(my_books=Count('books')).filter(my_books__gt=0).order_by('name')

Review.objects.values('book__title', 'rating').filter(rating__gt=3)

BookG.objects.values('title').filter(reviews__isnull=True)

BookG.objects.annotate(reviews_count=Count('reviews')).order_by('-reviews_count')

BookG.objects.filter(title__icontains='Куба').order_by('author__name')

Author.objects.annotate(num_books=Count('books')).filter(num_books__gt=2).order_by('num_books')

Review.objects.filter(rating__gt=4).order_by('book', 'rating')

BookG.objects.filter(reviews__isnull=True).order_by('title')

BookG.objects.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')

# найди авторов, у которых есть хотя бы одна книга с более чем 100 страницами
Author.objects.filter(books__pages__gt='100').distinct()

# подсчитать средний рейтинг книг и отстртитоватьв убывающем порядке
BookG.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

# найти книги у которых больше двух жанров
BookG.objects.filter(genres__gt=2).distinct()

# найти книгоу у которой название содержит подстроку 'Фантастика' и рейтинг большет 3
BookG.objects.filter(genres__name__contains='Фантастика', reviews__rating__gt=3).distinct()

Genre.objects.annotate(count_books=Count('books'))

# подсчитать количество рецензий для каждого автора
Author.objects.annotate(count_revs=Count('books__reviews'))

BookG.objects.filter(reviews__rating__gt=4).distinct()

Genre.objects.annotate(count_bs=Count('books'))

BookG.objects.filter(genres__isnull=True)

BookG.objects.order_by('-pages').first()

BookG.objects.annotate(av_rate=Avg('reviews__rating'))

BookG.objects.filter(Q(author__name__icontains='Че Гевара') & Q(genres__name__contains='Фантастика'))

# Сначала данные группируются и сорт. по первому полю. Затем внутри каждой группы выполняется сорт. по следующему полю.
BookG.objects.all().order_by('pages', 'created_at')

BookG.objects.filter(reviews__rating__gt=3).update(Case(When(author='Иван', then=Value('черновик'))))

BookG.objects.filter(reviews__isnull=True)


Author.objects.filter(Q(books__pages__gt=250) & Q(books__reviews__isnull=False)).distinct()
# равны
Author.objects.filter(books__pages__gt=250, books__reviews__isnull=False).distinct()

BookG.objects.filter(genres__gt=1).annotate(average_rate=Avg('reviews__rating')).filter(average_rate__gt=3)

#  Для проверки условий на разных книгах (или других связанных объектах) нужно использовать
#  аннотации с фильтром и агрегацию.
authors = Author.objects.annotate(
    books_with_high_pages=Count('books', filter=Q(books__pages__gt=300)),
    books_with_high_rating=Count('books', filter=Q(books__reviews__rating__gt=4))
).filter(
    books_with_high_pages__gt=0,  # Есть хотя бы одна книга с > 300 страниц
    books_with_high_rating__gt=0  # Есть хотя бы одна книга с рейтингом > 4
)

Author.objects.annotate(all_books=Count('books')).filter(Q(all_books=1) & Q(books__title__icontains='Че'))
# равны
Author.objects.annotate(all_books=Count('books')).filter(all_books=1, books__title__icontains='Че')

BookG.objects.filter(Q(genres__name__contains='Детектив') & Q(reviews__isnull=True)).distinct()

Genre.objects.filter(books__pages__lt=100).distinct()

BookG.objects.annotate(count_reviews=Count('reviews', filter=Q(reviews__rating__lt=3))).order_by('-count_reviews')

Author.objects.filter(books__reviews__isnull=False).distinct()

BookG.objects.filter(pages__gt=500).annotate(avg_review_rate=Avg('reviews__rating')).order_by('-avg_review_rate')

# Вывести авторов, у которых есть хотя бы одна книга, не относящаяся ни к одному жанру
# , и при этом эта книга имеет отзыв с рейтингом выше 4.
Author.objects.filter(books__genres__isnull=True, books__reviews__rating__gt=4).distinct()

# Найди авторов, у которых есть хотя бы одна книга с рейтинг. обзора выше 4, и при этом у этой книги больше 300 страниц.
Author.objects.filter(books__pages__gt=300, books__reviews__rating__gt=4).distinct()

# Найди жанры, которые связаны хотя бы с одной книгой, которая имеет рейтинг обзора выше 3 и меньше 100 страниц.
Genre.objects.filter(books__reviews__rating__gt=3, books__pages__lt=100).distinct()
# равны
Genre.objects.filter(Q(books__reviews__rating__gt=3) & Q(books__pages__lt=100)).distinct()

# Выведи книги, у которых нет отзывов, но они были созданы в прошлом году (используй поле date_create)
one_year_ago = timezone.now() - timedelta(days=365)
BookG.objects.filter(Q(date_create__lt=one_year_ago) & Q(reviews__isnull=True))

# Найди авторов, у которых есть хотя бы одна книга, написанная более 5 лет назад, и которая имеет больше 500 страниц.
five_year_ago = timezone.now() - timedelta(days=365*5)
Author.objects.filter(Q(books__date_create__lt=five_year_ago) & Q(books__pages__gt=500))

# Выведи книги, у которых средний рейтинг обзоров меньше 3, но эти книги принадлежат хотя бы двум жанрам.
BookG.objects.annotate(av_rate=Avg('reviews__rating'), book_genres=Count('genres')).filter(Q(av_rate__lte=3) & Q(book_genres__gt=1))

# Выведи авторов, у которых есть хотя бы одна книга, в которой рейтинг обзора выше 3, но при этом книга не имеет жанра.
Author.objects.filter(Q(books__genres__isnull=True) & Q(books__reviews__rating__gt=3)).distinct()

# Найди книги, у которых более 2 отзывов с рейтингом ниже 2.
BookG.objects.annotate(count_rev=Count('reviews', filter=Q(reviews__rating__lt=2))).filter(count_rev__gt=2).distinct()

# Найди жанры, которые связаны с книгами, в которых хотя бы один обзор имеет рейтинг 5 и книга имеет больше 400 страниц
Genre.objects.filter(Q(books__pages__gt=400) & Q(books__reviews__rating=5)).distinct()

# Найди авторов, которые не написали книг с рейтингом ниже 2, и у которых хотя бы одна книга с более чем 300 страницами.
Author.objects.exclude(Q(books__reviews__rating__lt=2)).filter(books__pages__gt=300)

# Найди книги, которые имеют отзывы, но для которых нет ни одного отзыва с рейтингом выше 3.
BookG.objects.filter(Q(reviews__isnull=False)).distinct().annotate(max_rate=Max('reviews__rating')).exclude(max_rate__gt=3)

# Найди авторов, у которых есть книги с рейтингом обзора больше 4 и страницами больше 300.
Author.objects.filter(books__reviews__rating__gt=4, books__pages__gt=300).distinct()

#Найди книги, которые имеют рейтинг в отзывах больше 3, имеют жанр "Детектив" и были созданы более 2 лет назад.
from dateutil.relativedelta import relativedelta
from django.utils import timezone
two_year = timezone.now() - relativedelta(years=2)
BookG.objects.filter(genres__name__contains='Детектив', reviews__rating__gt=3, created_at__gt=two_year).distinct()

# Найди жанры, в которых есть хотя бы одна книга с отзывами, где рейтинг меньше 2 и книга имеет меньше 200 страниц.
Genre.objects.filter(books__reviews__rating__lt=2, books__pages__lt=200).distinct()

# Выведи авторов, у которых есть книги, не относящиеся к жанрам, но с рейтингом отзывов выше 4.
Author.objects.filter(books__genres__isnull=True, books__reviews__gt=4).distinct()

# Найди книги, у которых хотя бы один отзыв с рейтингом меньше 3 и книга относится к жанрам, имеющим более 3 книг.
# - я незнаю как сделать один запросс както нужно отдельно подсчитать количество книг к каждому жанру.. могу в два запроса
genres_more_3_books = Genre.objects.values('name').annotate(all_books=Count('books')).filter(all_books__gt=3)
BookG.objects.filter(reviews__rating__lt=3, genres__in=genres_more_3_books).distinct()

# Найди книги, которые имеют отзывы с рейтингом больше 4 и страниц больше 500, но у которых нет жанра.
BookG.objects.filter(genres__isnull=True, reviews__rating__gt=4, pages__gt=500)

# Выведи жанры, которые связаны с книгами, в которых хотя бы один отзыв имеет рейтинг ниже 3 и книга была опубликована в прошлом году.
one_year = timezone.now() - relativedelta(years=1)
Genre.objects.filter(books__reviews__rating__lt=3, books__created_at__gt=one_year).distinct()
# если необходимо посмотреть за прошлый календарный год
Genre.objects.filter(books__reviews__rating__lt=3, books__created_at__year__lt=2024).distinct()

# Найди авторов, чьи книги не имеют жанров, но в которых есть отзывы с рейтингом больше 4.
Author.objects.filter(books__genres__isnull=True, books__reviews__rating__gt=4).distinct()

# Найди книги с рейтингом в отзывах меньше 2, страницами больше 100, где жанры не указаны.
BookG.objects.filter(reviews__rating__lt=2, pages__gt=100, genres__isnull=True).distinct()

# Выведи авторов, у которых есть книги с более чем 3 жанрами и рейтинг в отзывах которых выше 3.
Author.objects.annotate(count_genres=Count('books__genres')).filter(count__genres__gt=3, books__reviews__rating__gt=3)

# Найди книги, которые имеют отзывы с рейтингом больше 4 и страниц больше 500, но у которых нет жанра.
BookG.objects.filter(genres__isnull=True, reviews__rating__gt=4, pages__gt=500)

# Выведи жанры, которые связаны с книгами, в которых хотя бы один отзыв имеет рейтинг ниже
# 3 и книга была опубликована в прошлом году.
one_year = timezone.now() - relativedelta(years=1)
Genre.objects.filter(books__reviews__rating__lt=3, books__created_at__gt=one_year).distinct()
# если нужна привязка не к отрезку год а к календарному году
Genre.objects.filter(books__reviews__rating__lt=3, books__created_at__year__lt=2024).distinct()

# Используя Case и When, найдите книги, у которых рейтинг в отзывах выше 4, и добавьте новое поле с названием
# "Рейтинг_отличный", которое будет иметь значение "Да", если рейтинг больше 4, и "Нет", если меньше или равен 4.
BookG.objects.annotate(Рейтинг_отличный=Case(When(reviews__rating__gt=4, then=Value('Да')),
                                             When(reviews__rating__lte=4, then=Value('Нет')),
                                             output_field=CharField()))

# Найдите авторов, у которых книги были созданы в 2022 году и имеют более 300 страниц. Примените Case и When для создания
# нового поля "Долгий_путь", которое будет равно "Да", если книга больше 500 страниц, и "Нет", если меньше.
Author.objects.values('name').filter(books__created_at__year=2022, books__pages__gt=300).annotate(Долгий_путь=Case(When(books__pages__gt=500, then=Value('Да')), When(books__pages__lt=500, then=Value('Нет')), output_field=CharField()))
# в вопросе стоит найти автором но анотировать книги, я просил задания без селект\префетч релейтед а тут кажется он...
# потому что если я пробую просто анотировать поле и применять фильтры к обратной связи ForeignKey а в связанных моделях
# есть поля и больше 300 и меньше и поэтому всегда выдаёт результат нет...

# Используя Q и фильтры, найдите книги, которые имеют рейтинг в отзывах больше 3 или страницы больше 400.
# Используйте комбинацию условий с Q.
BookG.objects.filter(Q(reviews__rating__gt=3) | Q(pages__gt=400)).distinct()

# Используя агрегацию, найдите жанры, в которых средний рейтинг по отзывам выше 4, а количество книг больше 5.
Genre.objects.annotate(avg_rate=Avg('books__reviews__rating'), count_books=Count('books')).filter(avg_rate__gt=4, count_books__gt=5)

# Используя агрегации и фильтрацию через F, найдите книги, в которых количество страниц больше, чем рейтинг в отзывах
# в этом моменте не понятно чем максимальный\средний\сумма рейтинг? предположу что сумма рейтингов
BookG.objects.annotate(sum_rate=Sum('reviews__rating')).filter(sum_rate__lt=F('pages'))

# Найдите авторов, у которых есть книги, созданные в 2019 году или позднее, и количество отзывов на книгу больше 10.
# Используйте агрегации для подсчёта количества отзывов
Author.objects.annotate(all_rev=Count('books__reviews')).filter(books__created_at__year__gt=2019, all_rev__gt=10).distinct()

# Используя Case и When, создайте поле, которое будет определять, является ли книга "популярной" (если средний рейтинг
# больше 4 и количество отзывов больше 20), или "непопулярной".
BookG.objects.annotate(avg_rating=Avg('reviews__rating'), count_reviews=Count('reviews'), popular=Case(When(Q(avg_rating__gt=4) & Q(count_reviews__gt=20), then=Value('популярная')), default=Value('непопулярная'), output_field=CharField()))

# Найдите книги, которые были созданы в определённом временном диапазоне (например, с 2020 по 2022) и имеют рейтинг отзыва
# больше 3. Используйте фильтрацию по датам и условию рейтинга.
BookG.objects.filter(created_at__year__range=[2020, 2022], reviews__rating__gt=3)

# Используя Q, найдите авторов, у которых есть книги с рейтингом меньше 2 и страницами больше 100.
Author.objects.filter(Q(books__reviews__rating__lt=2) & Q(books__pages__gt=100)).distinct()

# Используя F и агрегацию, найдите жанры, где количество книг с более чем 500 страницами превышает 3.
# в голову приходит только как с помощю Q решить
Genre.objects.annotate(book_500=Count('books', filter=Q(books__pages__gt=500))).filter(Q(book_500__gt=3))

# Используя Case и When, добавьте в выборку книги, где новый столбец "Рейтинг_книги" будет равен 1, если рейтинг книги
# выше 4, и 0 в противном случае
# тут тоже непонятно какой рейтинг суммарный\средний\максимальный? предположим что средний
BookG.objects.annotate(avg_rating=Avg('reviews__rating'), Рейтинг_книги=Case(When(avg_rating__gt=4,then=Value(1)), default=Value(0), output_field=IntegerField()))

# Найдите книги, у которых количество страниц больше 400 и они были созданы в течение последнего года. Используйте
# фильтрацию по датам и количеству страниц.
# one_year = timezone.now() - relativedelta(years=1)
BookG.objects.filter(pages__gt=400, created_at__gt=one_year)

# Найдите авторов, чьи книги имеют хотя бы один отзыв с рейтингом выше 4, а также они создали книги в прошлом году.
# Используйте фильтрацию по датам и рейтингу отзывов.
Author.objects.filter(books__reviews__rating__gt=4, books__created_at__year__lt=2024).distinct()

# Используя Case и When, добавьте новое поле "Возраст_автора", которое будет вычисляться как разница между текущей датой
# и годом рождения автора, и отобразите только тех, у кого возраст больше 30 лет.
date_now = timezone.now()
authors = Author.objects.annotate(
    age=ExpressionWrapper(
        (date_now.year - F('birthday__year')) -
        ((date_now.month, date_now.day) < (F('birthday__month'), F('birthday__day'))),
        output_field=IntegerField()
    )
)

# Найдите книги, которые были опубликованы в течение определённого периода времени (например, с января по май) и имеют
# менее 100 страниц. Используйте фильтрацию по датам и количеству страниц.
BookG.objects.filter(pages__lt=100, created_at__year=2024, created_at__month__range=[1, 5])

# Добавь к книгам поле Popularity с помощью Case и When:
# Значение "High", если средний рейтинг выше 4 и количество отзывов больше 50.
# "Medium", если рейтинг от 3 до 4 и отзывов от 20 до 50.
# "Low" в остальных случаях.
books = BookG.objects.annotate(avg_rate=Avg('reviews__rating'), count_revs=Count('reviews'), Popularity=Case(
                                    When(avg_rate__gt=4, count_revs__gt=50, then=Value('High')),
                                    When(avg_rate__range=[3, 4], count_revs__range=[20, 50], then=Value('Medium')),
                                    default=Value('Low'), output_field=CharField()))

# Найди книги, опубликованные в течение последних двух лет, где количество страниц больше максимального рейтинга отзывов,
# умноженного на 50. Используй аннотацию и F.
two_years_ago = timezone.now() - relativedelta(years=2)
BookG.objects.annotate(max_rate=Max('reviews__rating')).filter(Q(pages__gt=F('max_rate') * 50)) & Q(created_at__gt=two_year)

# Выведи жанры, которые связаны с книгами, где хотя бы 30% отзывов имеют рейтинг ниже 2.
from django.db.models.functions import Round
genres = Genre.objects.annotate(count_reviews=Count('reviews'), reviews_abow_two=Count('books',
                    filter=Q(books__reviews__rating__lt=2)),
                    percent=ExpressionWrapper(F('reviews_abow_two') * 1.0 / F('count_reviews') * 100,
                    output_field=FloatField())).annotate(round_precent=Round('percent', 2)).filter(round_precent__gt=30)

# Аннотируй жанры полем TopBookRating, которое будет содержать максимальный рейтинг книги из жанра, и выведи жанры,
# где TopBookRating выше среднего рейтинга всех книг.
avg_all_books_rating = BookG.objects.aggregate(avg_rating=Avg('reviews__rating'))['avg_rating']
Genre.objects.annotate(TopBookRating=Max('books__reviews__rating')).filter(TopBookRating__gt=avg_all_books_rating)

# Добавь к авторам поле BooksWeight, которое будет суммой страниц всех их книг. Выведи только тех авторов, у которых
# это значение превышает 10 000.
Author.objects.annotate(BooksWeight=Sum('books__pages')).filter(BooksWeight__gt=10000)

#Найди книги, где количество отзывов с рейтингом 5 больше, чем количество отзывов с рейтингом 1. Исп. аннотацию и фильтры.
BookG.objects.annotate(reviews_five=Count('reviews', filter=Q(reviews__rating=5)), reviews_one=Count('reviews',
                                        filter=Q(reviews__rating=1))).filter(reviews_five__gt=F('reviews_one'))

# Добавь к книгам поле OldOrRecent, которое будет показывать:"Old",
# если книга создана больше 5 лет назад."Recent", если меньше.
five_year = timezone.now() - relativedelta(years=5)
BookG.objects.annotate(OldOrRecent=Case(When(created_at__lt=five_year, then=Value('Old')),
                                  When(created_at__gt=five_year, then=Value('Recent')), output_field=CharField()))

# Выведи авторов, у которых есть хотя бы одна книга, где количество отзывов меньше, чем количество страниц.
BookG.objects.annotate(rev_count=Count('reviews')).filter(rev_count__lt=F('pages'))

# Добавь к книгам поле ReviewRateDifference, которое будет содержать разницу между максимальным и минимальным рейтингом
# отзывов. Отфильтруй книги, у которых эта разница больше 2.
BookG.objects.annotate(max_rate=Max('reviews__rating'), min_rate=Min('reviews__rating'),
                                             ReviewRateDifference=ExpressionWrapper(F('max_rate') - F('min_rate'),
                                             output_field=IntegerField())).filter(ReviewRateDifference__gt=2)

# Выведи жанры, у которых суммарное количество страниц книг больше среднего количества страниц всех книг.
avg_pages_all = BookG.objects.aggregate(avg_pages=Avg('pages'))['avg_pages']
Genre.objects.annotate(avg_pages_genre=Avg('books__pages')).filter(avg_pages_genre__gt=avg_pages_all)

# Добавь к авторам поле AverageBookRating, которое будет средним рейтингом всех их книг. Найди авторов, у которых это
# значение ниже среднего рейтинга всех книг всех авторов.
avg_all_rating = BookG.objects.aggregate(rate=Avg('reviews__rating'))['rate']
Author.objects.annotate(AverageBookRating=Avg('books__reviews__rating')).filter(AverageBookRating__lt=avg_all_rating)

# Найди книги, которые были созданы в течение посл месяца и имеют больше отзывов с рейтингом 5, чем книг, созданных
# в тот же период, но с рейтингом 3.
month = timezone.now() - relativedelta(months=1)
BookG.objects.filter(created_at__gt=month).annotate(reviews_five_count=Count('reviews__rating',
                            filter=Q(reviews__rating=5)), reviews_three_count=Count('reviews',
                            filter=Q(reviews__rating=3))).filter(reviews_five_count__gt=F('reviews_three_count'))
