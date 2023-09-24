from django.db import models

from foodcartapp.models import Order, Restaurant


class Distance(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        on_delete=models.CASCADE,
        related_name='distances'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='заказ',
        on_delete=models.CASCADE,
        related_name='distances'
    )
    interval = models.FloatField(
        'расстояние',
        blank=True,
        null=True,
    )
    date = models.DateField('дата расчёта расстояния')

    class Meta:
        verbose_name = 'расстояние'
        verbose_name_plural = 'расстояния'
        ordering = ['interval']

    def __str__(self):
        return f'{self.restaurant} - {self.interval}km'
