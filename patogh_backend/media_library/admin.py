from django.contrib import admin

from .models import PdfItem, Podcast, PodcastEpisode


@admin.register(PdfItem)
class PdfItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'created_at']
    list_filter = ['published']
    search_fields = ['title', 'description']


class PodcastEpisodeInline(admin.TabularInline):
    model = PodcastEpisode
    extra = 1
    fields = ['title', 'part_number', 'audio_file']


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'created_at']
    list_filter = ['published']
    search_fields = ['title', 'description']
    inlines = [PodcastEpisodeInline]


@admin.register(PodcastEpisode)
class PodcastEpisodeAdmin(admin.ModelAdmin):
    list_display = ['title', 'podcast', 'part_number', 'created_at']
    list_filter = ['podcast']
    search_fields = ['title']
    autocomplete_fields = []
