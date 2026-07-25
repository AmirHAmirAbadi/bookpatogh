from django.db import transaction
from django.db.models import F

from rest_framework import serializers

from catalog.models import Book
from .models import GatewaySettings, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    # Accepts the book's id under `id` on write (source=book_id), exactly like
    # the CART array items the frontend already builds: {id, title, price,
    # emoji, qty}. Also readable on the way out (not write_only) so admins
    # looking at an existing order can see which catalog book each line item
    # refers to, not just its price/title snapshot.
    #
    # SECURITY: `title`, `price` and `emoji` are NOT accepted from the
    # client. They are always looked up from the Book row on the server, so
    # a tampered request can never buy a book below its real price (or make
    # up items for books that don't exist).
    id = serializers.CharField(source='book_id', required=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'title', 'price', 'emoji', 'qty']
        read_only_fields = ['title', 'price', 'emoji']
        extra_kwargs = {
            'qty': {'min_value': 1},
        }

    def validate(self, attrs):
        book_id = attrs.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError({'id': 'کتاب مورد نظر پیدا نشد.'})

        qty = attrs.get('qty', 1)
        if book.stock < qty:
            raise serializers.ValidationError({'qty': f'موجودی «{book.title}» کافی نیست.'})

        # Overwrite anything the client sent with the real, trusted values.
        attrs['title'] = book.title
        attrs['price'] = book.final_price
        attrs['emoji'] = book.emoji
        attrs['_book'] = book
        return attrs


class GatewaySettingsSerializer(serializers.ModelSerializer):
    is_configured = serializers.BooleanField(read_only=True)

    class Meta:
        model = GatewaySettings
        fields = ['merchant_id', 'is_configured', 'updated_at']
        read_only_fields = ['updated_at', 'is_configured']

    def validate_merchant_id(self, value):
        value = value.strip()
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'phone', 'postal_code', 'address',
            'gateway', 'total', 'status', 'items', 'created_at',
            'payment_status', 'ref_num',
        ]
        # SECURITY: `total` is server-computed from the real item prices,
        # never trusted from the client — otherwise a customer could submit
        # any `total` they like regardless of what's actually in the cart.
        # `payment_status`/`ref_num` are only ever written by the Zarinpal
        # callback view after a real server-to-server verification with the
        # bank (see views.ZarinpalCallbackView) — never by the client.
        read_only_fields = [
            'id', 'total', 'status', 'created_at',
            'payment_status', 'ref_num',
        ]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data.pop('total', None)  # ignore any client-sent value, just in case
        request = self.context.get('request')
        customer = None
        if request and request.user and request.user.is_authenticated:
            customer = request.user

        # Re-check stock under the transaction (locking the rows) so two
        # concurrent orders can't both succeed against the same last copy.
        for item in items_data:
            book = Book.objects.select_for_update().get(id=item['_book'].id)
            if book.stock < item['qty']:
                raise serializers.ValidationError({'items': f'موجودی «{book.title}» کافی نیست.'})
            item['_book'] = book

        computed_total = sum(item['price'] * item['qty'] for item in items_data)
        order = Order.objects.create(customer=customer, total=computed_total, **validated_data)

        for item in items_data:
            item.pop('book_id', None)
            book = item.pop('_book')
            OrderItem.objects.create(order=order, book=book, **item)
            # توجه: موجودی انبار اینجا کم نمی‌شود. تا وقتی پرداخت واقعاً توسط
            # زرین‌پال تایید نشده (نگاه کن به orders.views.ZarinpalCallbackView)
            # این فقط یک سفارشِ «در انتظار پرداخت» است، نه یک خرید قطعی؛ اگر
            # همین‌جا موجودی کم می‌شد، سفارش‌های ناموفق/رهاشده برای همیشه
            # موجودی کتاب را کم نگه می‌داشتند.

        return order
