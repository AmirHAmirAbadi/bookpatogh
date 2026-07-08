from django.contrib import admin

from .models import BookRequest


@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'text']
    list_editable = ['status']
