from django.db import models
from django.utils.text import slugify

from patogh_backend.idgen import generate_id

DIRECTION_CHOICES = [
    ('rtl', 'راست‌به‌چپ (فارسی)'),
    ('ltr', 'چپ‌به‌راست (انگلیسی)'),
]


class Post(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    title = models.CharField('عنوان', max_length=300)
    content = models.TextField('متن')
    direction = models.CharField('جهت نوشتار', max_length=3, choices=DIRECTION_CHOICES, default='rtl')
    published = models.BooleanField('منتشر شده', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # آدرس خوانا برای صفحه‌ی سئوی این پست.
    slug = models.SlugField('نامک (Slug)', max_length=350, unique=True, allow_unicode=True, blank=True, editable=False)

    class Meta:
        verbose_name = 'پست وبلاگ'
        verbose_name_plural = 'پست‌های وبلاگ'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or 'پست'
            self.slug = f'{base}-{self.id}'
        super().save(*args, **kwargs)


class Comment(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    post = models.ForeignKey(Post, verbose_name='مطلب', related_name='comments', on_delete=models.CASCADE)
    name = models.CharField('نام', max_length=100, blank=True, default='')
    content = models.TextField('متن دیدگاه')
    approved = models.BooleanField('تأیید شده', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دیدگاه'
        verbose_name_plural = 'دیدگاه‌ها'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name or "کاربر مهمان"}: {self.content[:30]}'
