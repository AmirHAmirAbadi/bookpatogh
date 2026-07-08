from rest_framework import viewsets, permissions

from .models import BookRequest
from .serializers import BookRequestSerializer


class IsAdminOrCreateOnly(permissions.BasePermission):
    """Anyone can submit a request (POST); only staff can list/view/edit/delete them."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class BookRequestViewSet(viewsets.ModelViewSet):
    queryset = BookRequest.objects.all()
    serializer_class = BookRequestSerializer
    permission_classes = [IsAdminOrCreateOnly]
    lookup_field = 'id'
