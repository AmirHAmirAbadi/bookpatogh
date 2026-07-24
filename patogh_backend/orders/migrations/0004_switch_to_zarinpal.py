from django.db import migrations, models


def set_gateway_to_zarinpal(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.update(gateway='zarinpal')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_gatewaysettings_order_payment_status_order_ref_num_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gatewaysettings',
            old_name='terminal_id',
            new_name='merchant_id',
        ),
        migrations.AlterField(
            model_name='gatewaysettings',
            name='merchant_id',
            field=models.CharField(
                blank=True,
                help_text='کد پذیرنده‌ای که زرین‌پال هنگام ثبت‌نام درگاه به شما داده است (یک کد ۳۶ کاراکتری).',
                max_length=64,
                verbose_name='کد پذیرنده (Merchant ID)',
            ),
        ),
        migrations.RenameField(
            model_name='order',
            old_name='sep_token',
            new_name='authority',
        ),
        migrations.AlterField(
            model_name='order',
            name='authority',
            field=models.CharField(
                blank=True, default='', max_length=100, verbose_name='کد Authority درگاه زرین‌پال',
            ),
        ),
        migrations.RemoveField(
            model_name='order',
            name='trace_no',
        ),
        migrations.AlterField(
            model_name='order',
            name='ref_num',
            field=models.CharField(
                blank=True, default='', max_length=60, verbose_name='شماره پیگیری تراکنش (Ref ID)',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='gateway',
            field=models.CharField(
                choices=[('zarinpal', 'زرین‌پال')], default='zarinpal', max_length=40, verbose_name='درگاه پرداخت',
            ),
        ),
        migrations.RunPython(set_gateway_to_zarinpal, noop_reverse),
    ]
