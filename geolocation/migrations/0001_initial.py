# Generated by Django 4.1 on 2022-10-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес')),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='широта')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='долгота')),
                ('updated_at', models.DateTimeField(verbose_name='дата запроса к геокодеру')),
            ],
        ),
    ]
