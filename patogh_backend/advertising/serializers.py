from rest_framework import serializers

from .models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = [
            'id', 'page', 'position', 'media_type', 'media',
            'link_url', 'active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
