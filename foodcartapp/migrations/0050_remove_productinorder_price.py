# Generated by Django 3.2.15 on 2023-09-19 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_productinorder_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinorder',
            name='price',
        ),
    ]