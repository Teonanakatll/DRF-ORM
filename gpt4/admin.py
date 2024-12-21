from django.contrib import admin

from gpt4.models import BookG, Author, Review


@admin.register(BookG)
class BookGAdmin(admin.ModelAdmin):
    pass

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass