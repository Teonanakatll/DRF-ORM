from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from gpt4.utils import cons
from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    # настройка django_filter, ?price=..., ?search=..., ?ordering=price
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # поле для фильтрации
    filterset_fields = ['price']
    # поиск имеет смысл если поиск осуществляется по двум полям, если поле одно то достаточно фильтра
    search_fields = ['name', 'author_name']
    # поля для сортировки
    ordering_fields = ['price', 'author_name']

    # чтобы при добавлении новой книги автоматически добавлять в качестве хозяина книги аккаунт добавивший её для этого
    #  переопределяем метод perform_create() который вызывается в методе create() вьюсета при создании новой записи
    def perform_create(self, serializer):
        # перед проверкой в сериализаторе находятся необработанные данные serializer.initial_data
        # обращаемся к словарю validated_data который появляется в сериализаторе если данные прошли волидацию и сработал
        # serializer.is_valid() иначе он вернёт False и появляется коллекция serializer.errors
        # так как у нас установлен permission_class, берём юзера из self.request.user
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


# в случае с patch(), put() сериалайзер работает только на вход валидируя поля прописанные в модели
class UserBookRelationView(mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer

    # псевдоним поля id в запросе переопределяем, чтобы не запутаться так как передаём id не данной модели а связи с моделью Book
    lookup_field = 'book'

    # так как это промежуточная модель то чтобы найти нужную запись нужно передать id записи на это неудобно потому что придётся гдето хранить
    # id всех записей но так как это промежуточная таблица мы можем найти запись по юзеру и книге. или находим или создаём
    # ЕСЛИ ЭТУ КНИГУ НЕ ЛАЙКАЛИ ТО СОЗДАЁМ ЭТУ СВЯЗЬ И ЕНДПОИНТ НА POST ЗАПРОС ДЛЯ СОЗДАНИЯ ЗАПИСИ НАМ ПРОСТО НЕ НУЖЕН!!!!!!!!
    def get_object(self):
        #
        obj, created = UserBookRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])

        return obj


def auth(request):
    return render(request, 'oauth.html')
