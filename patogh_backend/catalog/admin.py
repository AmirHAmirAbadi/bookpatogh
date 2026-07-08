from django.contrib import admin

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'discount', 'stock', 'category', 'featured', 'category2', 'created_at']
    list_filter = ['category', 'featured', 'category2']
    search_fields = ['title', 'author__name']
    autocomplete_fields = ['author']
