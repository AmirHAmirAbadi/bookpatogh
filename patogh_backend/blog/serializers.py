from rest_framework import serializers

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    # Kept as `date` (ISO datetime) to match the original object's field name.
    # Frontend should render it with: new Date(p.date).toLocaleDateString('fa-IR')
    date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'direction', 'published', 'date', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'name', 'content', 'approved', 'date']
        # Guests can create/read comments but must never flip their own
        # `approved` flag; only staff (via PUT, which requires is_staff)
        # can moderate. The view also forces approved=True on creation.
        read_only_fields = ['approved']

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('متن دیدگاه نمی‌تواند خالی باشد.')
        return value

    def validate_name(self, value):
        return (value or '').strip()
