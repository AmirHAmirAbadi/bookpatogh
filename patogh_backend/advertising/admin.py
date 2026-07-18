from django.contrib import admin

from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['page', 'position', 'media_type', 'active', 'updated_at']
    list_filter = ['page', 'position', 'media_type', 'active']
