# Generated by Django 4.1 on 2022-11-02 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='restaurant',
            new_name='fulfilling_restaurant',
        ),
    ]