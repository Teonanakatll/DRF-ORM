from django.db.models import Count
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend
from .models import BookG

# да кстати то что параметры извлекаются вручную это значительное отличие, пока я не сталкнулся с реальной задачей где
# я это могу применить смысл немного замыливается но я запишу это как пример и может когданебудь пригодиться, а на счет
# большей гибкости ты миеешь в виду что я могу в filter_backends например создавать временные анотации\агрегации и ид
# для промежуточных вычислений и без всяких lookup_expr получать всё на что у меня хватит фантазии передать в запросе и
# использовать?

# сложные вычисления нельзя реализовать напрямую через filterset_class, поскольку django_filters не позволяет в
# стандартном фильтре использовать агрегации или сложные вычисления.
class BookGFilterSet(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    # author_name = filters.CharFilter(method='filter_author_name')
    author_name = filters.CharFilter(field_name='author__name', lookup_expr='icontains')
    min_pages = filters.NumberFilter(field_name='pages', lookup_expr='gte')
    max_pages = filters.NumberFilter(field_name='pages', lookup_expr='lte')

    # def filter_author_name(self, queryset, name, value):
    #     if not isinstance(value, str):
    #         return queryset   # пропустить фильтр если знчение не строка
    #     return queryset.filter(author__name__icontains=value)

    class Meta:
        model = BookG
        fields = ['title', 'author_name', 'min_pages', 'max_pages']

class BookGFilterBackends(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        # проверяем есть ли параметры в запроссе
        author_imya = request.query_params.get('author_imya', None)
        reviews_min_count = request.query_params.get('reviews_min_count', None)

        if reviews_min_count is not None:   # проверку на None пройдёт всё что не None - 0/''/[]/False
            # добавляем аннотацию
            queryset = queryset.annotate(review_count=Count('review'))
            # фильтруем по минимальному количеству рецензий
            queryset = queryset.filter(reviews__count__gt=reviews_min_count)

        # return queryset

        if author_imya:
            return queryset.filter(author__name__icontains=author_imya)
        return queryset
