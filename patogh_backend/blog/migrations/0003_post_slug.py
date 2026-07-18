# Generated manually to add an SEO-friendly "slug" field to Post.

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.all():
        base = slugify(post.title, allow_unicode=True) or 'پست'
        post.slug = f'{base}-{post.id}'
        post.save(update_fields=['slug'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, default='', max_length=350, verbose_name='نامک (Slug)'),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, noop_reverse),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, editable=False, max_length=350, unique=True, verbose_name='نامک (Slug)'),
        ),
    ]
