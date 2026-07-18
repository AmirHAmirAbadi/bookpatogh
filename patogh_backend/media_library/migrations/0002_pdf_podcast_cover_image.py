from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdfitem',
            name='cover_image',
            field=models.FileField(blank=True, default='', upload_to='pdf_covers/', verbose_name='عکس جلد'),
        ),
        migrations.AddField(
            model_name='podcast',
            name='cover_image',
            field=models.FileField(blank=True, default='', upload_to='podcast_covers/', verbose_name='عکس جلد'),
        ),
    ]
