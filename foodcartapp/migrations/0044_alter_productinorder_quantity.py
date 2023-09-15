# Generated by Django 3.2.15 on 2023-09-09 23:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_alter_productinorder_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinorder',
            name='quantity',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='too small number')], verbose_name='количество'),
        ),
    ]
