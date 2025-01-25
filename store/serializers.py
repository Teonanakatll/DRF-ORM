from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


# сериализация это преобразования объектов Python в json, десериализация обратный процесс

# создаём отдельный сериализатор который будет вложенным для связи MTM прямая связь через поле 'readers',
# и будет выводить информацию о связанных моделях, сериалайзер сам выберет поля указанные в fields
class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BooksSerializer(ModelSerializer):
    # likes_count = serializers.SerializerMethodField()

    # read_only=True - только для чтения, его не нужно передавать с POST/PUT/PATCH
    annotated_likes = serializers.IntegerField(read_only=True)

    # так как это кеширующее поле его необходимо выводить с параметром read_only=True
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)

    # в source= через точечную анотацию идём по связям owner.client.username чтобы указать источник данных,
    # default= значение если поле пустое, будет дополнительный запросс
    # owner_name = serializers.CharField(source='owner.username', default='', read_only=True)
    owner_name = serializers.CharField(read_only=True)

    # добавляем в поля вложенный сериализатор, так как он сер. данные поля 'readers' прямой связи MTM он должен
    # называться readers, можно придумать любое название но в source указать кокой у него источник
    readers_abc = BookReaderSerializer(many=True, source='readers', read_only=True)

    # также source указывается если результат вычислен в методе модели ИЛИ мы хотим назвать поле по ДРУГОМУ
    # total_pages = serializers.IntegerField(source='get_total_pages', read_only=True)  # 'get_total_pages' — метод мод.

    class Meta:
        model = Book
        # readers_abc - вложенный сериализатор
        fields = ('id', 'name', 'price', 'author_name', 'owner_name', 'annotated_likes', 'rating', 'readers_abc')

    # instance - книга которую мы в данный момент сериализуем, создаст дополнительный запрос в бд для каждой записи
    # def get_likes_count(self, instance):
    #     return UserBookRelation.objects.filter(book=instance, like=True).count()



class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        # апи предпологается для юзеров так что юзера будем брать из request (чтоб он не подставил другого)
        fields = ('book', 'like', 'in_bookmarks', 'rate', 'comment')