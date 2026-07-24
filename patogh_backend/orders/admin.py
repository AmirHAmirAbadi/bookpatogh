from django.contrib import admin

from .models import GatewaySettings, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'title', 'price', 'emoji', 'qty']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone', 'total', 'gateway', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'gateway']
    search_fields = ['id', 'customer_name', 'phone', 'ref_num']
    list_editable = ['status']
    readonly_fields = ['payment_status', 'authority', 'ref_num']
    inlines = [OrderItemInline]


@admin.register(GatewaySettings)
class GatewaySettingsAdmin(admin.ModelAdmin):
    """رزرو راه دوم برای ویرایش شناسه پذیرنده: از همین پنل جنگو هم قابل تغییر
    است، نه فقط از صفحه‌ی «اتصال» در اپ فروشگاه."""
    list_display = ['merchant_id', 'updated_at']

    def has_add_permission(self, request):
        # singleton: هیچ‌وقت اجازه‌ی ساخت رکورد دوم را نده
        return not GatewaySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
