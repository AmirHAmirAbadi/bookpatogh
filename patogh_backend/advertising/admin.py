from django.contrib import admin

from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'page', 'position', 'media_type', 'active', 'link_url', 'pos_x', 'pos_y', 'width', 'height', 'updated_at']
    list_filter = ['page', 'position', 'media_type', 'active']
