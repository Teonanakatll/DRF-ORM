from django.contrib.auth.models import User, AnonymousUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from gpt4.models import BookG, Author, Genre, UserBookGRelation, Review

from gpt4.utils import cons


# Автоматическое создание документации для API с помощью пакетов, таких как drf-yasg или django-rest-swagger
#
#
# сериализаторы для фильтрации

# Основные компоненты Swagger:
# Swagger UI
# Это красивая веб-страница с документацией API.
# Ты можешь видеть все эндпоинты, их параметры и тестировать их прямо на месте.
# Пример:
#
# Swagger Editor
# Это редактор, где ты можешь вручную описывать спецификацию OpenAPI.
#
# Swagger Codegen
# Генератор кода для клиента или сервера API.
# Например, ты можешь на основе описания API сгенерировать клиент для React, Python или даже другой сервер.

# class BookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BookG
#         fields = '__all__'
#         depth = 1  # Это автоматически подтянет связанные модели
# — это параметр в Meta классе ModelSerializer, который автоматически добавляет вложенные данные для связанных моделей.
# Значение указывает, насколько глубоко нужно заглянуть в связи.

class BookGLinkSerializer(ModelSerializer):
    """Служит для отрисовки названия книги и ссылки на неё в модели Genre"""
    # слаг передаётся для формирования красивого урла на фронте
    book_slug = serializers.CharField(required=False, source='slug')
    cover_url = serializers.SerializerMethodField()
    book_url = serializers.HyperlinkedIdentityField(view_name='bookg-detail')

    class Meta:
        model = BookG
        fields = ('id', 'title', 'book_slug', 'cover_url', 'book_url')

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover:
            return request.build_absolute_uri(obj.cover.url)

class GenreLinkSerializer(ModelSerializer):
    """Служит для отрисовки имени и ссылки в модели BookG"""

    # required=False - оставляем возможность редактировать его, но делаем поле
    # необязательным для отправки на сервер тк оно автоинкрементируется через slugify,
    genre_slug = serializers.CharField(required=False, source='slug')

    # HyperlinkedIdentityField предназначено для создания ссылки на текущий объект. Оно автоматически возвращает URL,
    # ведущий на детальный эндпоинт (detail-view) текущего объекта.
    genre_url = serializers.HyperlinkedIdentityField(view_name='genre-detail')

    class Meta:
        model = Genre
        fields = ('id', 'name', 'genre_slug', 'genre_url')

class GenreSerializer(ModelSerializer):
    """Основной сериализатор жанров"""

    # required=False - оставляем возможность редактировать его, но делаем поле
    # необязательным для отправки на сервер тк оно автоинкрементируется через slugify,
    genre_slug = serializers.CharField(required=False, source='slug')

    # тут мы используем поле только для отрисовки связанных записей поэтому нам не нужно делать отдельное поле
    # PrimaryKeyRelatedField() чтобы иметь возможность изменять через запросс это поле
    book_list = BookGLinkSerializer(many=True, required=False, source='books')

    class Meta:
        model = Genre
        fields = ('id', 'name', 'genre_slug', 'description', 'book_list')

# class AuthorLinkSerializer(ModelSerializer):
#     author_slug = serializers.CharField(required=False, source='slug')
#     author_link = serializers.HyperlinkedIdentityField(view_name='author_detail')
#     class Meta:
#         model = Author
#         fields = ('id', 'name', 'author_slug', 'author_link')

def delete_old_file(instance, field_name):
    '''функция удаляет старое фото при добавлении нового'''
    file = getattr(instance, field_name)
    if file:
        file.delete(save=False)


class BookGSerializer(ModelSerializer):
    # required=False - оставляем возможность редактировать его, но делаем поле
    # необязательным для отправки на сервер тк оно автоинкрементируется через slugify,
    book_slug = serializers.CharField(required=False, source='slug')

    # формируем полный урл к фото с помощю метода, SerializerMethodField() - только для чтения
    cover_url = serializers.SerializerMethodField()
    # указываем что поле только для записи и необязательное
    cover = serializers.ImageField(write_only=True, required=False)

    # клиенту отправляется отформатированное поле created_at изменённое в to_representation()
    # Если в модели поле типа DateField, то сериализатор будет возвращать объект datetime.date.
    # Это объект, который представляет только дату без времени
    view_created_at = serializers.DateTimeField(read_only=True)
    # view_created_at = serializers.DateField(format='%Y-%m-%d')  # Указываем формат

    # данное поле на самом деле с автоинкрементом поэтому просто пример поля только для чтения и не обязательное
    created_at = serializers.DateTimeField(write_only=True, required=False)

    # вложенный сериалайзер ТОЛЬКО ДЛЯ ОТРИСОВКИ СВЯЗАННЫХ ЖАНРОВ - PrimaryKeyRelatedField позволяет изменять по id
    # "Возьми данные из связи genres, но при этом используй GenreSerializer для отрисовки вместо списка id"
    book_genres = GenreLinkSerializer(read_only=True, source='genres', many=True)

    # тк поле добавленно в source другого поля
    # добавления или изменения связей через ManyToManyField или обратной связи ForeignKey в
    # запросах, PrimaryKeyRelatedField это поле, которое позволяет работать со связанными объектами через их id
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), required=False, many=True)

    #  Установка read_only=True гарантирует, что это поле нельзя будет изменить через API.Пользователь сможет только
    #  видеть его значение. Использование read_only=True для вычисляемых или кеширующих полей — это способ защитить
    #  данные и обеспечить их целостность. Это защищает бизнес-логику от вмешательства и гарантирует, что данные в
    #  системе всегда актуальны и соответствуют ожиданиям.
    avg_hate_rate = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    annotated_likes = serializers.IntegerField(read_only=True)


    # source='owner' - это позволяет использовать owner_name в сериализаторе (на выходе), в то время как на входе
    # сериализатор продолжает работать с полем owner модели.  сериализатор ожидает owner как поле для записи
    owner_name = serializers.CharField(source='owner', read_only=True)

    # Только для чтения: Поле предназначено исключительно для отображения данных при сериализации. Оно не обрабатывает
    # входные данные при создании или обновлении объекта.
    author_name = serializers.ReadOnlyField(source='author.name')

    author_slug = serializers.ReadOnlyField(source='author.slug')

    # HyperlinkedRelatedField предназначено для создания ссылки на связанный объект.
    author_url = serializers.HyperlinkedRelatedField(
        view_name='author-detail',  # Это имя view, которое будет использоваться для создания URL
        read_only=True,  # Значение этого поля нельзя будет изменять в запросах
        source='author'  # Это поле в модели, которое связывается с этим полем сериализатора
    )

    # так как мы указали это поле в sourct другого поля, чтобы принимать данные этого поля нам необхдиммо обьявить
    # PrimaryKeyRelatedField()
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), required=False, write_only=True)


    # HyperlinkedModelSerializer

    # HyperlinkedIdentityField предназначено для создания ссылки на текущий объект. Оно автоматически возвращает URL,
    # ведущий на детальный эндпоинт (detail-view) текущего объекта.
    # url = serializers.HyperlinkedIdentityField(view_name='bookg-detail')

    class Meta:
        model = BookG
        fields = ('id', 'title', 'book_slug', 'cover_url', 'cover', 'content', 'author', 'author_name', 'author_slug', 'author_url', 'owner_name', 'pages', 'annotated_likes', 'avg_hate_rate', 'view_created_at', 'created_at', 'genres', 'book_genres')

    # Старые файлы не удаляются сами, необходимо обрабатывать удаление вручную
    def update(self, instance, validated_data):
        if 'cover' in validated_data:
            delete_old_file(instance, 'cover')
        return super().update(instance, validated_data)

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover:
            return request.build_absolute_uri(obj.cover.url)
        return 'У книги нет обложки'

    # добавляем валидацию чтобы проверить существует ли owner в базе данных
    # def validate_owner(self, value):
    #     # Проверяем, что пользователь не анонимный
    #     if not isinstance(value, User):
    #         raise ValidationError("Owner must be a valid user.")
    #     return value

    # def validate_owner(self, value):
    #     # Проверяем, что пользователь не анонимный
    #     if not User.objects.filter(id=value.id).exists():
    #         raise ValidationError("Указанный автор не существует")
    #     return value

    # этот метод меняет представление данных возвращаемых в товете
    def to_representation(self, instance):
        # переопределяем метод сериализатора чтобы переопределить поля
        representation = super().to_representation(instance)

        representation['view_created_at'] = instance.created_at.date()  # возвращаем только дату

        # чтобы не выводить дополнительно список id который возвращается сериализатором по умолчанию для поля мтм, но
        # так как поле обязатьельно нужно указать в сериалайзере чтобы присвоить ему валидатор PrimaryKeyRelatedField,
        # то мы просто берём данные без ключа вложенного сериализатора и вставляем в стандартное поле
        representation['genres'] = representation.pop('book_genres')

        return representation

class UserBookGRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookGRelation
        fields = ('id', 'book', 'user', 'like', 'in_bookmarks', 'hate_rate')

class UserSerializer(ModelSerializer):
    my_books = BookGLinkSerializer(many=True, required=False, source='owner_books')
    read_list = BookGLinkSerializer(many=True, required=False, source='readers_books')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_staff', 'my_books', 'read_list')

class ReviewSerializer(ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'content', 'book', 'user', 'rating', 'created_at', 'is_anonymous')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # переопределяем поле возвращаем только дату
        representation['created_at'] = instance.created_at.date()

        return representation

class AuthorSerializer(ModelSerializer):
    author_slug = serializers.CharField(required=False, source='slug')
    book_list = BookGLinkSerializer(many=True, required=False, source='books')
    class Meta:
        model = Author
        fields = ('id', 'name', 'author_slug', 'birthday', 'biography', 'book_list')