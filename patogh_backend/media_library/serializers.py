from rest_framework import serializers

from .models import PdfItem, Podcast, PodcastEpisode


class PdfItemSerializer(serializers.ModelSerializer):
    # `file` already gives the raw (inline-servable) URL of the upload.
    # `download_url` points at the dedicated download endpoint, which sends
    # the response with `Content-Disposition: attachment` so clicking it
    # always triggers an actual file download instead of opening a browser
    # preview tab, regardless of which origin the storefront is hosted on.
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = PdfItem
        fields = [
            'id', 'title', 'description', 'emoji', 'cover_image', 'file', 'download_url',
            'published', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        url = f'/api/pdfs/{obj.id}/download/'
        return request.build_absolute_uri(url) if request else url


class PodcastEpisodeSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = PodcastEpisode
        fields = [
            'id', 'podcast', 'title', 'part_number', 'audio_file',
            'download_url', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if not obj.audio_file:
            return None
        url = f'/api/podcast-episodes/{obj.id}/download/'
        return request.build_absolute_uri(url) if request else url


class PodcastSerializer(serializers.ModelSerializer):
    # Read-only nested list so the frontend gets a podcast + all its parts
    # in a single request; episodes themselves are created/edited/deleted
    # through their own `/api/podcast-episodes/` endpoint.
    episodes = PodcastEpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Podcast
        fields = [
            'id', 'title', 'description', 'emoji', 'cover_image', 'published',
            'episodes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
