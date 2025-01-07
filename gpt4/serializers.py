from django.contrib.auth.models import User, AnonymousUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from gpt4.models import BookG, Author, Genre, UserBookGRelation

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

class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

class BookGSerializer(ModelSerializer):
    # клиенту отправляется отформатированное поле created_at изменённое в to_representation()
    view_created_at = serializers.DateTimeField(read_only=True)

    # данное поле на самом деле с автоинкрементом поэтому просто пример поля только для чтения и не обязательное
    created_at = serializers.DateTimeField(write_only=True, required=False)

    # вложенный сериалайзер ДЛЯ ОТРИСОВКИ СВЯЗАННЫХ ЖАНРОВ
    book_genres = GenreSerializer(read_only=True, source='genres', many=True)

    # добавления или изменения связей через ManyToManyField или обратной связи ForeignKey в
    # запросах, обычно используют PrimaryKeyRelatedField
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), required=False, many=True)

    class Meta:
        model = BookG
        fields = ('id', 'title', 'content', 'author', 'owner', 'pages', 'avg_hate_rate', 'view_created_at', 'created_at', 'genres', 'book_genres')

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
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_staff')
