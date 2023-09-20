# Generated by Django 3.2.15 on 2023-09-20 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('0', 'Необработанный'), ('1', 'Принят'), ('2', 'Готовится'), ('3', 'Доставляется'), ('4', 'Исполнен')], db_index=True, default=0, max_length=2, verbose_name='статус'),
        ),
    ]
