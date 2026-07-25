from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from catalog.models import Book
from .models import GatewaySettings, Order
from .zarinpal_gateway import START_PAY_URL, ZarinpalError, request_payment, verify_payment
from .serializers import GatewaySettingsSerializer, OrderSerializer


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
    throttle_scope = None  # فقط اکشن start_payment زیر آن را (به 'payment') override می‌کند

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items').all()
        # لیست اصلیِ «سفارش‌ها» در پنل ادمین فقط سفارش‌های واقعاً پرداخت‌شده
        # را نشان می‌دهد. سفارش‌هایی که پرداختشان ناموفق مانده یا کاربر اصلاً
        # به درگاه وصل نشده، اینجا دیده نمی‌شوند — آن‌ها در سربرگ جداگانه‌ی
        # «رد شده‌ها» (اکشن rejected زیر) نشان داده می‌شوند.
        if self.action == 'list':
            return qs.filter(payment_status='paid')
        if self.action == 'rejected':
            return qs.exclude(payment_status='paid')
        # retrieve / start_payment / partial_update / destroy: باید بتوانند
        # سفارش را با هر وضعیتی پیدا کنند (مثلاً یک سفارش pending برای تلاش
        # دوباره‌ی پرداخت).
        return qs

    @action(detail=False, methods=['get'])
    def rejected(self, request):
        """سربرگ «رد شده‌ها»: سفارش‌هایی که پرداختشان ناموفق بوده یا هرگز
        تکمیل نشده (کاربر به درگاه وصل نشد یا وسط راه رهایش کرد)."""
        qs = self.get_queryset().order_by('-created_at')
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True, methods=['post'], url_path='start-payment',
        permission_classes=[permissions.AllowAny],  # مشتری مهمان هم باید بتواند سفارش خودش را پرداخت کند
        throttle_classes=[ScopedRateThrottle], throttle_scope='payment',
    )
    def start_payment(self, request, id=None):
        """مرحله‌ی «PaymentRequest»: مرورگر بعد از گرفتن Authority از این‌جا،
        خودش به آدرس StartPay هدایت می‌شود تا وارد صفحه‌ی واقعی زرین‌پال شود."""
        order = self.get_object()

        if order.payment_status == 'paid':
            return Response({'detail': 'این سفارش قبلاً پرداخت شده است.'}, status=400)

        gw = GatewaySettings.load()
        if not gw.is_configured:
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status'])
            return Response(
                {'detail': 'درگاه پرداخت هنوز از پنل مدیریت (بخش «اتصال») متصل نشده است.'},
                status=400,
            )

        # SECURITY: مبلغ همیشه از order.total خوانده می‌شود — یعنی همان مبلغی
        # که سرور، نه مرورگر، هنگام ثبت سفارش از روی قیمت واقعی کتاب‌ها محاسبه
        # کرده (نگاه کن به OrderSerializer.create). زرین‌پال به ریال کار
        # می‌کند و سایت به تومان، پس اینجا ضربدر ۱۰ می‌شود.
        amount_rial = order.total * 10
        callback_url = request.build_absolute_uri(reverse('zarinpal-callback'))

        try:
            authority = request_payment(
                gw.merchant_id, amount_rial,
                description=f'پرداخت سفارش {order.id}',
                callback_url=callback_url,
            )
        except ZarinpalError as exc:
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status'])
            return Response({'detail': str(exc)}, status=502)

        order.authority = authority
        order.save(update_fields=['authority'])
        return Response({'authority': authority, 'start_pay_url': START_PAY_URL.format(authority=authority)})


class IsStaffUser(permissions.BasePermission):
    """Only logged-in staff (the admin panel) may read or change gateway settings.
    A payment gateway merchant ID is store-configuration, not public data."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class GatewaySettingsView(APIView):
    """صفحه‌ی «اتصال» در پنل ادمین از همین‌جا کد پذیرنده را می‌خواند/ذخیره می‌کند."""
    permission_classes = [IsStaffUser]

    def get(self, request):
        obj = GatewaySettings.load()
        return Response(GatewaySettingsSerializer(obj).data)

    def put(self, request):
        obj = GatewaySettings.load()
        serializer = GatewaySettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ZarinpalCallbackView(APIView):
    """
    آدرسی که زرین‌پال بعد از پرداخت (موفق یا ناموفق)، مرورگر کاربر را با یک
    GET به آن برمی‌گرداند (پارامترهای Authority و Status).

    SECURITY: هرگز فقط بر اساس پارامترهایی که در همین درخواست از مرورگر کاربر
    می‌رسند (که به‌سادگی قابل جعل هستند) سفارش را «پرداخت‌شده» علامت نمی‌زنیم؛
    قبل از آن حتماً با verify_payment یک تایید server-to-server مستقیم از خودِ
    زرین‌پال می‌گیریم که با همان مبلغ واقعی سفارش انجام می‌شود.

    این ویو هیچ‌وقت به کاربر لاگین/توکن نیاز ندارد — چون خودِ درخواست از
    مرورگر کاربر برمی‌گردد، نه از یک کاربر احرازهویت‌شده در سایت ما.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'payment'

    def get(self, request):
        return self._handle(request.query_params)

    def post(self, request):
        return self._handle(request.data)

    def _handle(self, data):
        authority = data.get('Authority') or data.get('authority')
        status_param = data.get('Status') or data.get('status')

        if not authority:
            return HttpResponseRedirect('/app/#/payment-result?status=error')

        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(authority=authority)
            except Order.DoesNotExist:
                return HttpResponseRedirect('/app/#/payment-result?status=error')

            # Idempotency: اگر این سفارش قبلاً با موفقیت verify شده، دوباره به
            # زرین‌پال درخواست نزن (که هم غیرلازم است هم در برابر callback
            # تکراری از قبل امن است)؛ فقط همان نتیجه‌ی قبلی را نشان بده.
            if order.payment_status == 'paid':
                return HttpResponseRedirect(f'/app/#/payment-result?order={order.id}&status=success')

            if status_param != 'OK':
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status'])
                return HttpResponseRedirect(f'/app/#/payment-result?order={order.id}&status=failed')

            gw = GatewaySettings.load()
            amount_rial = order.total * 10
            verify_result = verify_payment(gw.merchant_id, amount_rial, authority)

            order.payment_status = 'paid' if verify_result.get('success') else 'failed'
            if verify_result.get('ref_id') is not None:
                order.ref_num = str(verify_result['ref_id'])
            order.save(update_fields=['payment_status', 'ref_num'])

            if order.payment_status == 'paid':
                # فقط همین‌جا، بعد از تاییدِ واقعیِ زرین‌پال، موجودی کتاب‌ها
                # کم می‌شود — نه هنگام ثبت اولیه‌ی سفارش.
                for item in order.items.all():
                    if item.book_id:
                        Book.objects.filter(id=item.book_id).update(stock=F('stock') - item.qty)
                        Book.objects.filter(id=item.book_id, stock__lt=0).update(stock=0)

        result_status = 'success' if order.payment_status == 'paid' else 'failed'
        return HttpResponseRedirect(f'/app/#/payment-result?order={order.id}&status={result_status}')
