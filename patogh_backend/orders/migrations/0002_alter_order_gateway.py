from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='gateway',
            field=models.CharField(
                choices=[('sep', 'درگاه بانک سامان (SEP)')],
                default='sep',
                max_length=40,
                verbose_name='درگاه پرداخت',
            ),
        ),
    ]
