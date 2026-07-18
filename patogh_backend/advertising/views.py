from rest_framework import viewsets, permissions

from .models import Advertisement
from .serializers import AdvertisementSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can read the (active) ad slots; only staff can manage them."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class AdvertisementViewSet(viewsets.ModelViewSet):
    serializer_class = AdvertisementSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        qs = Advertisement.objects.all()
        user = self.request.user
        if user and user.is_authenticated and user.is_staff:
            return qs
        # بازدیدکننده‌های عادی فقط باکس‌های فعال و دارای فایل را می‌بینند
        return qs.filter(active=True).exclude(media='')
