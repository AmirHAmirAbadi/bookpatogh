from django.conf import settings
from django.db import models

from catalog.models import Book
from patogh_backend.idgen import generate_order_no

STATUS_CHOICES = [
    ('در حال بررسی', 'در حال بررسی'),
    ('در حال ارسال', 'در حال ارسال'),
    ('تحویل داده شد', 'تحویل داده شد'),
    ('لغو شد', 'لغو شد'),
]

GATEWAY_CHOICES = [
    ('zarinpal', 'زرین‌پال'),
]


PAYMENT_STATUS_CHOICES = [
    ('pending', 'در انتظار پرداخت'),
    ('paid', 'پرداخت‌شده'),
    ('failed', 'ناموفق/لغوشده'),
]


class Order(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default=generate_order_no, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='کاربر', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='orders',
    )
    customer_name = models.CharField('نام گیرنده', max_length=200)
    phone = models.CharField('شماره موبایل', max_length=20)
    postal_code = models.CharField('کد پستی', max_length=15)
    address = models.TextField('آدرس')
    gateway = models.CharField('درگاه پرداخت', max_length=40, choices=GATEWAY_CHOICES, default='zarinpal')
    total = models.PositiveIntegerField('مبلغ کل (تومان)', default=0)
    status = models.CharField('وضعیت', max_length=30, choices=STATUS_CHOICES, default='در حال بررسی')
    created_at = models.DateTimeField(auto_now_add=True)

    # --- وضعیت پرداخت درگاه زرین‌پال ------------------------------------
    # این‌ها جدا از `status` بالا هستند: `status` مرحله‌ی ارسال/تحویل فیزیکی
    # سفارش است (که ادمین دستی تغییرش می‌دهد)، ولی این فیلدها مخصوص خودِ
    # تراکنش بانکی‌اند و فقط توسط بک‌اند (بعد از تایید واقعی از سمت زرین‌پال)
    # ست می‌شوند؛ کاربر یا مرورگر هیچ‌وقت مستقیم این‌ها را عوض نمی‌کند.
    payment_status = models.CharField(
        'وضعیت پرداخت', max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending',
    )
    authority = models.CharField('کد Authority درگاه زرین‌پال', max_length=100, blank=True, default='')
    ref_num = models.CharField('شماره پیگیری تراکنش (Ref ID)', max_length=60, blank=True, default='')

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.id


class GatewaySettings(models.Model):
    """
    تنظیمات اتصال به درگاه پرداخت زرین‌پال (صفحه‌ی «اتصال» در پنل ادمین).
    این یک مدل تک‌رکوردی (singleton) است: همیشه فقط همان رکورد با pk=1
    خوانده/نوشته می‌شود، تا فقط یک تنظیمات درگاه فعال برای کل سایت وجود داشته باشد.
    """
    merchant_id = models.CharField(
        'کد پذیرنده (Merchant ID)', max_length=64, blank=True,
        help_text='کد پذیرنده‌ای که زرین‌پال هنگام ثبت‌نام درگاه به شما داده است (یک کد ۳۶ کاراکتری).',
    )
    updated_at = models.DateTimeField('آخرین ذخیره', auto_now=True)

    class Meta:
        verbose_name = 'تنظیمات درگاه پرداخت'
        verbose_name_plural = 'تنظیمات درگاه پرداخت'

    def __str__(self):
        return 'تنظیمات درگاه پرداخت'

    def save(self, *args, **kwargs):
        self.pk = 1  # همیشه همان یک رکورد را بازنویسی کن، نه رکورد جدید
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def is_configured(self):
        return bool(self.merchant_id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=300)   # snapshot, kept even if the book is later edited/deleted
    price = models.PositiveIntegerField()
    emoji = models.CharField(max_length=10, blank=True, default='📚')
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.title} × {self.qty}'
