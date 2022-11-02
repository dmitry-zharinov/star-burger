# Generated by Django 4.1 on 2022-11-01 18:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_order_comment_alter_orderitem_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='количество'),
        ),
    ]