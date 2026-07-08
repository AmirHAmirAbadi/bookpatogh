from rest_framework import viewsets, permissions

from .models import Order
from .serializers import OrderSerializer


class IsAdminOrCreateOnly(permissions.BasePermission):
    """Anyone (guest checkout included) can place an order (POST);
    only staff can list all orders, view details, change status, or delete."""

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrCreateOnly]
    lookup_field = 'id'
