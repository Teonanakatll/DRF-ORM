from django.db.models import Count
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BooksSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    annotated_likes = serializers.IntegerField()

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'owner', 'likes_count', 'annotated_likes')

    # instance - книга которую мы в данный момент сериализуем
    def get_likes_count(self, instance):
        return UserBookRelation.objects.filter(book=instance, like=True).count()



class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        # апи предпологается для юзеров так что юзера будем брать из request (чтоб он не подставил другого)
        fields = ('book', 'like', 'in_bookmarks', 'rate', 'comment')