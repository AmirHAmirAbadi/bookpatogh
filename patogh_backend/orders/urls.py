from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GatewaySettingsView, OrderViewSet, ZarinpalCallbackView

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('settings/gateway/', GatewaySettingsView.as_view(), name='gateway-settings'),
    path('payments/zarinpal/callback/', ZarinpalCallbackView.as_view(), name='zarinpal-callback'),
] + router.urls
