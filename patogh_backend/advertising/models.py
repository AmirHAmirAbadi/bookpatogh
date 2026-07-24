from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from patogh_backend.idgen import generate_id

# هر صفحه‌ای که قرار است تبلیغ روی آن نمایش داده شود، اینجا تعریف می‌شود.
PAGE_CHOICES = [
    ('home', 'صفحه اصلی'),
    ('shop', 'فروشگاه'),
    ('authors', 'نویسندگان'),
    ('contact', 'تماس با ما'),
    ('checkout', 'ثبت نهایی پرداخت'),
]

# این‌ها فقط یک میان‌بر برای پرکردن سریع pos_x/pos_y هستند (وقتی ادمین روی یکی
# از دکمه‌های آماده در پنل کلیک می‌کند)؛ محدودیتی روی تعداد یا یکتا بودن ایجاد
# نمی‌کنند و بعداً هم می‌شود با کشیدن (drag) دستی تغییرشان داد.
POSITION_CHOICES = [
    ('top-left', 'بالا - چپ'),
    ('top-right', 'بالا - راست'),
    ('middle-left', 'وسط - چپ'),
    ('middle-right', 'وسط - راست'),
    ('bottom-left', 'پایین - چپ'),
    ('bottom-right', 'پایین - راست'),
    ('custom', 'دلخواه (جابه‌جا شده با دست)'),
]

MEDIA_TYPE_CHOICES = [
    ('image', 'عکس'),
    ('video', 'فیلم بی‌صدا'),
]

PERCENT_VALIDATORS = [MinValueValidator(0), MaxValueValidator(100)]

# مختصات پیش‌فرض هر دکمه‌ی آماده (درصد از عرض/ارتفاع صفحه).
PRESET_POSITIONS = {
    'top-left': (1.0, 8.0),
    'top-right': (88.0, 8.0),
    'middle-left': (1.0, 42.0),
    'middle-right': (88.0, 42.0),
    'bottom-left': (1.0, 75.0),
    'bottom-right': (88.0, 75.0),
}


class Advertisement(models.Model):
    """
    یک تبلیغ نامرئی که فقط وقتی ادمین از داخل پنل مدیریت برایش عکس یا ویدیوی
    بی‌صدا آپلود کند، نمایش داده می‌شود. هر صفحه می‌تواند هر تعداد تبلیغ داشته
    باشد (محدودیتی در تعدادشان نیست).

    موقعیت و اندازه‌ی هر تبلیغ آزاد است و یا با انتخاب یکی از دکمه‌های آماده‌ی
    موقعیت (position) و یا با کشیدن/تغییر اندازه‌ی دستی روی یک پیش‌نمایش از
    صفحه در پنل مدیریت تنظیم می‌شود. pos_x/pos_y همیشه درصدی از عرض/ارتفاع
    صفحه‌ی نمایش هستند (نه پیکسل مطلق) تا روی صفحه‌نمایش‌های مختلف هم نسبتاً
    همان‌جا بماند.
    """
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    page = models.CharField('صفحه', max_length=20, choices=PAGE_CHOICES)
    position = models.CharField(
        'موقعیت (میان‌بر)', max_length=20, choices=POSITION_CHOICES, default='custom', blank=True,
    )
    media_type = models.CharField('نوع رسانه', max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    media = models.TextField('فایل (تصویر یا ویدیو)', blank=True, default='')
    link_url = models.URLField('لینک مقصد (اختیاری)', blank=True, default='')
    active = models.BooleanField('فعال', default=True)

    # درصدِ فاصله‌ی گوشه‌ی بالا-چپِ باکس از چپ/بالای صفحه. null یعنی «هنوز
    # دستی جابه‌جا نشده» — در save() بر اساس position یک مقدار پیش‌فرض منطقی
    # می‌گیرد.
    pos_x = models.FloatField(
        'فاصله از چپ (٪ عرض صفحه)', null=True, blank=True, validators=PERCENT_VALIDATORS,
    )
    pos_y = models.FloatField(
        'فاصله از بالا (٪ ارتفاع صفحه)', null=True, blank=True, validators=PERCENT_VALIDATORS,
    )
    width = models.PositiveIntegerField(
        'عرض (پیکسل)', default=150, validators=[MinValueValidator(60), MaxValueValidator(500)],
    )
    height = models.PositiveIntegerField(
        'ارتفاع (پیکسل)', default=300, validators=[MinValueValidator(60), MaxValueValidator(900)],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تبلیغ'
        verbose_name_plural = 'تبلیغات'
        ordering = ['page', '-created_at']

    def __str__(self):
        return f'{self.get_page_display()} / {self.get_position_display()} / {self.id}'

    def save(self, *args, **kwargs):
        if self.pos_x is None or self.pos_y is None:
            default_x, default_y = PRESET_POSITIONS.get(self.position, (1.0, 42.0))
            if self.pos_x is None:
                self.pos_x = default_x
            if self.pos_y is None:
                self.pos_y = default_y
        super().save(*args, **kwargs)
