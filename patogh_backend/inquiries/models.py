from django.db import models

from patogh_backend.idgen import generate_id


class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('در حال بررسی', 'در حال بررسی'),
        ('بررسی شد', 'بررسی شد'),
        ('رد شد', 'رد شد'),
    ]

    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    name = models.CharField('نام و نام خانوادگی', max_length=200)
    text = models.TextField('متن درخواست')
    status = models.CharField('وضعیت', max_length=30, choices=STATUS_CHOICES, default='در حال بررسی')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست'
        verbose_name_plural = 'درخواست‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.text[:30]}'
