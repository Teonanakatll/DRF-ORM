from django.db.models import Avg

from gpt4.utils import cons
from store.models import UserBookRelation


def set_rating(book):
    rating = UserBookRelation.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    # cons(rating)
    book.rating = rating
    book.save()
