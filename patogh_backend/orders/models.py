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

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=300)   # snapshot, kept even if the book is later edited/deleted
    price = models.PositiveIntegerField()
    emoji = models.CharField(max_length=10, blank=True, default='📚')
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.title} × {self.qty}'
