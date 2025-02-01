from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count, Case, When, IntegerField, F
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from gpt4.models import BookG, UserBookGRelation, Review, Genre, Author
from gpt4.my_custom_filters import BookGFilterSet, BookGFilterBackends
from gpt4.pagination import BookGPaginator
from gpt4.permissions import CreateOnlyAuthenticated, IsOwnerOrStaff, IsOwnerOrStaffOrReadOnly, IsStaffOrReadOnly, \
    IsUserOrStaffOrReadOnly
from gpt4.serializers import BookGSerializer, UserBookGRelationSerializer, UserSerializer, ReviewSerializer, \
    GenreSerializer, AuthorSerializer
from gpt4.utils import cons


class BookGViewSet(ModelViewSet):
    queryset = BookG.objects.annotate(annotated_likes=Count(Case(When(userbookgrelation__like=True, then=1), output_field=IntegerField())),
                                     owner_name=F('owner__username')).select_related('owner', 'author').prefetch_related('genres').order_by('id')
    serializer_class = BookGSerializer
    permission_classes = [CreateOnlyAuthenticated, IsOwnerOrStaffOrReadOnly]

    # в settings 'django_filter, ?pages=..., ?search=..., ?ordering=...
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, BookGFilterBackends]
    # поля для фильтрации
    # filterset_fields = ['pages']    # ЕСЛИ Я ДОБАВЛЮ НЕСКОЛЬКО ПОЛЕЙ?
    filterset_class = BookGFilterSet
    # поиск имеет смысл если он происходит по двум полям, если он проходит по одному полю то достаточно фильтра
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'id']
    pagination_class = BookGPaginator


    # Если не ModelViewSet или миксины, то в APIView данные файлов и фото извлекаются так
    # тоесть по сути формируем статус ответа, если и нужно добавить чтонебудь своё то всеравно лучше
    # это прописать во вьюсете или миксине, ведь в них уже настроенны ответы и респонс с данными модели

    #    # для парсинга изображений
    # parser_classes = (MultiPartParser, FormParser)

    # def post(self, request, *args, **kwargs):
    #     serializer = BookGSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)
    #
    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)
    #
    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)


    # этот метод вызывается в CreateView в методе create() POST запроса, после валидации данных но перед сохранением
    # обьекта, служит для добавления кастомной логики. автоматическае дабавление owner при создании книги

    def perform_create(self, serializer):
        if isinstance(self.request.user, User):
            serializer.validated_data['owner'] = self.request.user
            serializer.save()
        else:
            raise ValidationError("Owner must be a valid user.")

    # Когда ты используешь @action(detail=True), то ожидается, что pk (или идентификатор объекта) будет присутствовать
    # в URL. Например, если у тебя есть URL типа /books/{pk}/review/, то pk будет обязательным, так как detail=True.
    # Если pk=None, это означает, что можно вызвать метод без указания конкретного объекта, и в этом случае нужно
    # предусмотреть логику для работы с этим значением.
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def review(self, request, pk=None):
        book = self.get_object()

        revs = Review.objects.filter(book=book)

        # data используется для валидации и создания новых объектов, которые передаются из не сейф методов запросов
        # serializer = ReviewSerializer(data=data, many=True)
        # instance используется для сериализации существующих объектов.
        serializer = ReviewSerializer(instance=revs, many=True)  # или serializer = ReviewSerializer(revs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class UserBookGRelationVew(mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserBookGRelation.objects.all()
    serializer_class = UserBookGRelationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'book'

    # чтобы создвть эту модель коротая выступает промежуточной для MTM User/BookG для того чтобы найти или создать
    # экземпляр указываем юзера из запроса (который если отправил запросс значит авторизован) и id книги из урла
    # когда мы передаём id в урле то передаём его как args, но на сервер оно приходит как kwargs потому что добавляется
    # в словать request.kwargs как значение к ключу lookup_field, который мы установили как 'book'
    #
    # так как в этот раз работает метод update() PUT/PATCH запросы, я до вызова сериалайзера переопределяю метро
    # get_object() чтобы или получить или создать обьект используя реквест юзера и айди совсем другой модели, тоесть
    # если бы я запрашивал запись по айди данной модели метод получения записи переопределять не нужно было бы
    def get_object(self):
        # проверяем что существует книга с указанным id
        book = get_object_or_404(BookG, id=self.kwargs['book'])

        obj, create = UserBookGRelation.objects.update_or_create(user=self.request.user, book=book)
        return obj

class UserView(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.prefetch_related('owner_books', 'readers_books').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsUserOrStaffOrReadOnly]

    @action(detail=True, methods=['get'], serializer_class=BookGSerializer, url_path='books',
                                                                            permission_classes=[IsOwnerOrStaff])
    def list_books(self, request, pk=None):
        books = BookG.objects.filter(owner_id=pk)
        return Response(BookGSerializer(books, many=True).data, status=200)

class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.prefetch_related('books').all()
    serializer_class = GenreSerializer
    permission_classes = [IsStaffOrReadOnly]

class AuthorView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                                    mixins.UpdateModelMixin, GenericViewSet):
    queryset = Author.objects.prefetch_related('books').all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]