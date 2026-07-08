from rest_framework import serializers

from .models import BookRequest


class BookRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRequest
        fields = ['id', 'name', 'text', 'status', 'created_at']
        # `status` is set/changed by staff only (via the admin panel or a
        # PUT, both of which already require is_staff). Anyone could POST a
        # new request, so it must not be settable at creation time.
        read_only_fields = ['status', 'created_at']
