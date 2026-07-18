# Generated manually to add SEO-friendly "slug" fields to Book and Author.
# Adds the field loosely first, fills it in for every existing row, then
# tightens it to unique=True — this order keeps it safe on databases that
# already have data (no IntegrityError from a premature unique constraint).

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Book = apps.get_model('catalog', 'Book')
    Author = apps.get_model('catalog', 'Author')

    for author in Author.objects.all():
        base = slugify(author.name, allow_unicode=True) or 'نویسنده'
        author.slug = f'{base}-{author.id}'
        author.save(update_fields=['slug'])

    for book in Book.objects.all():
        base = slugify(book.title, allow_unicode=True) or 'کتاب'
        book.slug = f'{base}-{book.id}'
        book.save(update_fields=['slug'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_book_workshop'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, default='', max_length=250, verbose_name='نامک (Slug)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='book',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, default='', max_length=350, verbose_name='نامک (Slug)'),
            preserve_default=False,
        ),
        migrations.RunPython(populate_slugs, noop_reverse),
        migrations.AlterField(
            model_name='author',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, editable=False, max_length=250, unique=True, verbose_name='نامک (Slug)'),
        ),
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, editable=False, max_length=350, unique=True, verbose_name='نامک (Slug)'),
        ),
    ]
