from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from gpt4.models import BookG, UserBookGRelation, Review
from gpt4.my_custom_filters import BookGFilterSet, BookGFilterBackends
from gpt4.permissions import CreateOnlyAuthenticated
from gpt4.serializers import BookGSerializer, UserBookGRelationSerializer, UserSerializer
from gpt4.utils import cons
from store.permissions import IsOwnerOrStaffOrReadOnly


class BookGViewSet(ModelViewSet):
    queryset = BookG.objects.all().prefetch_related('genres')
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
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        book = self.get_object()
        # логика добавления рецензии
        review_text = request.data.get('content')
        review_rating = request.data.get('rating')


        review_anon = request.data.get('is_anonymous', False)  # берём значение или False по умолчанию
        is_anonymous = bool(review_anon) if isinstance(review_anon, (bool, str, int)) else False

        # if review_text and review_rating:
        #     review = Review.objects.create(book=book, user=request.user, content=review_text,
        #                                    rating=review_rating, is_anonymous=is_anonymous)

        # сериалайзер всё коректно отрабатывает и проверяет сам, в крайнем случае (хотя мне уже что создавать записи
        # нужно только через сериалайзер) в экшене вызываем full_clean() который подтянет все валидаторы из полей и по
        # сути отработает как и обычные валидаторы сериализатора, если в шеле не срабатывает валидация чойсов
        # и всех мест в коде где вручную будут создаваться записи и если
        # забыть вызвать full_clean() отработает кастомный валидатор модели
        if review_text and review_rating:
            review = Review(book=book, user=request.user, content=review_text,
                                           rating=review_rating, is_anonymous=is_anonymous)
            try:
                # проверяем валидацию на уровне модели
                review.full_clean()
                review.save()   # теперь сохраняем обьект если валидация прошла успешно

                return Response({'message': 'Review added successfully!'}, status=201)
            except ValidationError as e:
                return Response({'error': e.messages}, status=400)

            # return Response({'message': 'Review added successfully!'}, status=201)
        # return Response({'error': 'Review or rating missing'}, status=400)

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
        obj, create = UserBookGRelation.objects.update_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj

class UserView(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['get'], serializer_class=BookGSerializer, url_path='books',
                                                                            permission_classes=[AllowAny])
    def list_books(self, request, pk=None):
        books = BookG.objects.filter(owner_id=pk)
        return Response(BookGSerializer(books, many=True).data, status=200)
