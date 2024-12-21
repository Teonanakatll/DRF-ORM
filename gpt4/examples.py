from django.db.models import Count

from gpt4.models import BookG, Author, Review

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

