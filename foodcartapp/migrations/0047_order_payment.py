# Generated by Django 4.1 on 2022-10-13 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_order_called_at_order_created_at_order_delivered_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('NONE', 'Не указан'), ('CASH', 'Наличные'), ('CARD', 'Картой')], db_index=True, default='NONE', max_length=4, verbose_name='способ оплаты'),
        ),
    ]
