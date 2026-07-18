import django.db.models.deletion
import patogh_backend.idgen
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PdfItem',
            fields=[
                ('id', models.CharField(default=patogh_backend.idgen.generate_id, editable=False, max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, default='', verbose_name='توضیحات')),
                ('emoji', models.CharField(blank=True, default='📄', max_length=10, verbose_name='ایموجی')),
                ('file', models.FileField(upload_to='pdfs/', verbose_name='فایل PDF')),
                ('published', models.BooleanField(default=True, verbose_name='منتشر شده')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'پی‌دی‌اف',
                'verbose_name_plural': 'پی‌دی‌اف‌ها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.CharField(default=patogh_backend.idgen.generate_id, editable=False, max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300, verbose_name='عنوان')),
                ('description', models.TextField(blank=True, default='', verbose_name='توضیحات')),
                ('emoji', models.CharField(blank=True, default='🎙️', max_length=10, verbose_name='ایموجی')),
                ('published', models.BooleanField(default=True, verbose_name='منتشر شده')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'پادکست',
                'verbose_name_plural': 'پادکست‌ها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PodcastEpisode',
            fields=[
                ('id', models.CharField(default=patogh_backend.idgen.generate_id, editable=False, max_length=20, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=300, verbose_name='عنوان قسمت')),
                ('part_number', models.PositiveIntegerField(default=1, verbose_name='شماره قسمت')),
                ('audio_file', models.FileField(upload_to='podcasts/', verbose_name='فایل صوتی')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='media_library.podcast', verbose_name='پادکست')),
            ],
            options={
                'verbose_name': 'قسمت پادکست',
                'verbose_name_plural': 'قسمت‌های پادکست',
                'ordering': ['part_number', 'created_at'],
            },
        ),
    ]
