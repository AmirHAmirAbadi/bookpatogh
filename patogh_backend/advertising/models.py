from django.db import models

from patogh_backend.idgen import generate_id

# هر صفحه‌ای که قرار است باکس تبلیغاتی چپ/راست داشته باشد، اینجا تعریف می‌شود.
PAGE_CHOICES = [
    ('home', 'صفحه اصلی'),
    ('shop', 'فروشگاه'),
    ('authors', 'نویسندگان'),
    ('contact', 'تماس با ما'),
    ('checkout', 'ثبت نهایی پرداخت'),
]

POSITION_CHOICES = [
    ('left', 'چپ'),
    ('right', 'راست'),
]

MEDIA_TYPE_CHOICES = [
    ('image', 'عکس'),
    ('video', 'فیلم بی‌صدا'),
]


class Advertisement(models.Model):
    """
    یک باکس تبلیغاتی نامرئی در کنار صفحه (چپ یا راست) که فقط وقتی ادمین از
    داخل پنل مدیریت برایش عکس یا ویدیوی بی‌صدا آپلود کند، نمایش داده می‌شود.
    برای هر ترکیب (صفحه، موقعیت) فقط یک رکورد وجود دارد.
    """
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    page = models.CharField('صفحه', max_length=20, choices=PAGE_CHOICES)
    position = models.CharField('موقعیت', max_length=10, choices=POSITION_CHOICES)
    media_type = models.CharField('نوع رسانه', max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    media = models.TextField('فایل (تصویر یا ویدیو)', blank=True, default='')
    link_url = models.URLField('لینک مقصد (اختیاری)', blank=True, default='')
    active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تبلیغ'
        verbose_name_plural = 'تبلیغات'
        unique_together = ('page', 'position')
        ordering = ['page', 'position']

    def __str__(self):
        return f'{self.get_page_display()} / {self.get_position_display()}'
