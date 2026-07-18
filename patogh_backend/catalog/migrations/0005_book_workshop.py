# Generated manually to add the "workshop" flag to Book

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_book_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='workshop',
            field=models.BooleanField(default=False, verbose_name='محصول کارگاه'),
        ),
    ]
