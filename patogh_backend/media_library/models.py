from django.db import models

from patogh_backend.idgen import generate_id
from .validators import (
    AUDIO_EXTENSION_VALIDATOR,
    IMAGE_EXTENSION_VALIDATOR,
    PDF_EXTENSION_VALIDATOR,
    validate_audio_size,
    validate_image_size,
    validate_pdf_size,
)


class PdfItem(models.Model):
    """A single, always-free PDF that visitors can download directly.

    There is intentionally no price/discount field anywhere on this model:
    everything under the "پادکست و پی‌دی‌اف" section is free by design.
    """

    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    title = models.CharField('عنوان', max_length=300)
    description = models.TextField('توضیحات', blank=True, default='')
    emoji = models.CharField('ایموجی', max_length=10, default='📄', blank=True)
    cover_image = models.FileField(
        'عکس جلد', upload_to='pdf_covers/', blank=True, default='',
        validators=[IMAGE_EXTENSION_VALIDATOR, validate_image_size],
    )
    file = models.FileField(
        'فایل PDF', upload_to='pdfs/',
        validators=[PDF_EXTENSION_VALIDATOR, validate_pdf_size],
    )
    published = models.BooleanField('منتشر شده', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پی‌دی‌اف'
        verbose_name_plural = 'پی‌دی‌اف‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Podcast(models.Model):
    """A podcast "show" — a container for one or more downloadable/listenable
    episodes (parts). Always free, like the PDFs above."""

    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    title = models.CharField('عنوان', max_length=300)
    description = models.TextField('توضیحات', blank=True, default='')
    emoji = models.CharField('ایموجی', max_length=10, default='🎙️', blank=True)
    cover_image = models.FileField(
        'عکس جلد', upload_to='podcast_covers/', blank=True, default='',
        validators=[IMAGE_EXTENSION_VALIDATOR, validate_image_size],
    )
    published = models.BooleanField('منتشر شده', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پادکست'
        verbose_name_plural = 'پادکست‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PodcastEpisode(models.Model):
    """One part/episode of a podcast, with its own audio file."""

    id = models.CharField(primary_key=True, max_length=20, default=generate_id, editable=False)
    podcast = models.ForeignKey(Podcast, verbose_name='پادکست', related_name='episodes', on_delete=models.CASCADE)
    title = models.CharField('عنوان قسمت', max_length=300)
    part_number = models.PositiveIntegerField('شماره قسمت', default=1)
    audio_file = models.FileField(
        'فایل صوتی', upload_to='podcasts/',
        validators=[AUDIO_EXTENSION_VALIDATOR, validate_audio_size],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'قسمت پادکست'
        verbose_name_plural = 'قسمت‌های پادکست'
        ordering = ['part_number', 'created_at']

    def __str__(self):
        return f'{self.podcast.title} — {self.title}'
