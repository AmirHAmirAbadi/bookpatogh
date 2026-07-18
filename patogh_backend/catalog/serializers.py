from rest_framework import serializers

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'slug']


class AuthorNameField(serializers.SlugRelatedField):
    """
    Lets the API accept/return `author` as a plain name string, exactly like
    the original frontend objects (book.author === 'صادق هدایت'), instead of
    forcing the JS to deal with nested author objects or ids.
    If the author name doesn't exist yet, it's created automatically.
    """

    def to_internal_value(self, data):
        name = str(data).strip()
        if not name:
            self.fail('does_not_exist', slug_name=self.slug_field, value=name)
        author, _created = Author.objects.get_or_create(name=name)
        return author


class BookSerializer(serializers.ModelSerializer):
    author = AuthorNameField(slug_field='name', queryset=Author.objects.all())
    cover = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'price', 'discount', 'category',
            'category2', 'workshop', 'stock', 'emoji', 'images', 'cover', 'featured',
            'description', 'final_price', 'created_at', 'updated_at', 'slug',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def _absolute(self, url):
        if not url:
            return url
        if url.startswith('http://') or url.startswith('https://'):
            return url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('images'):
            data['images'] = [self._absolute(u) for u in data['images']]
        if data.get('cover'):
            data['cover'] = self._absolute(data['cover'])
        return data
