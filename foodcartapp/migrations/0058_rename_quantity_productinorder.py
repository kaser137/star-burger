# Generated by Django 3.2.15 on 2023-09-19 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_remove_order_amount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Quantity',
            new_name='ProductInOrder',
        ),
    ]