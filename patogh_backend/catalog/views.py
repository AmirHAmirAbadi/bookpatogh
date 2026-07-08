from rest_framework import viewsets, permissions

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can read the catalog; only staff (admin panel) can write to it."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'
