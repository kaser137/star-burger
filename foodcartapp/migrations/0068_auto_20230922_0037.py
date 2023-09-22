# Generated by Django 3.2.15 on 2023-09-21 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0067_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_orders', to='foodcartapp.order'),
        ),
        migrations.AlterField(
            model_name='productinorder',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products_in_orders', to='foodcartapp.product'),
        ),
    ]
