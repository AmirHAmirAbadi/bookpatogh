from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book', 'title', 'price', 'emoji', 'qty']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone', 'total', 'gateway', 'status', 'created_at']
    list_filter = ['status', 'gateway']
    search_fields = ['id', 'customer_name', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]
