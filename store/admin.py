from django.contrib import admin

from store.models import Book, UserBookRelation


@admin.register(Book)
class AdminBook(admin.ModelAdmin):
    pass

@admin.register(UserBookRelation)
class AdminBook(admin.ModelAdmin):
    pass
