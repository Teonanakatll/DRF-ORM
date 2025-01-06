from decimal import Decimal

from django.db.models import Avg

from gpt4.models import UserBookGRelation
from gpt4.utils import cons


def set_avg_hate_rate(book):
    # cons(book.avg_hate_rate)
    avg_hate_rate = UserBookGRelation.objects.filter(book=book).aggregate(av_rate=Avg('hate_rate')).get('av_rate')

    # тоесть ошибка возникает когда аггрегация ненаходит по книге связанных записей и в
    # итоге не может даже получить 0 а только None
    if avg_hate_rate == None:
        avg_hate_rate = Decimal('0.00')


    book.avg_hate_rate = avg_hate_rate
    # cons(book.avg_hate_rate)
    book.save()
