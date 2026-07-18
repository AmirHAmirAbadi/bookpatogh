from django.contrib import admin

from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'published', 'direction', 'created_at']
    list_filter = ['published', 'direction']
    search_fields = ['title', 'content']
    readonly_fields = ['slug']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'approved', 'created_at']
    list_filter = ['approved']
    search_fields = ['name', 'content']
    list_editable = ['approved']
