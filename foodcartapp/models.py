import requests
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from geopy import distance
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from star_burger import settings


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductInOrderQuerySet(models.QuerySet):
    @staticmethod
    def amount(pk):
        amount = ProductInOrder.objects.filter(
            order_id=pk).aggregate(amount=Sum(F('product__price') * F('quantity')))
        print(amount)
        return amount['amount']


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    STATUS = (
        ('0', 'Необработанный'),
        ('1', 'Принят'),
        ('2', 'Готовится'),
        ('3', 'Доставляется'),
        ('4', 'Исполнен'),
    )
    PAY_METHOD = (
        ('0', 'Наличностью'),
        ('1', 'Электронно'),
    )
    status = models.CharField(
        'статус',
        max_length=2,
        choices=STATUS,
        default=0,
        db_index=True
    )
    pay_method = models.CharField(
        'метод оплаты',
        max_length=2,
        choices=PAY_METHOD,
        db_index=True,
        blank=True,
        null=True,
    )
    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='ресторан',
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True
    )
    phonenumber = PhoneNumberField(
        'телефон',
        region='RU',
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
        null=True
    )
    registered_at = models.DateTimeField(
        'время регистрации',
        default=timezone.now
    )
    called_at = models.DateTimeField(
        'время звонка',
        null=True,
        blank=True
    )
    delivered_at = models.DateTimeField(
        'время доставки',
        null=True,
        blank=True
    )

    def amount(self):
        products = ProductInOrder.objects.filter(order=self.id)
        amount = 0
        for product in products:
            amount += product.price * product.quantity

        return amount

    amount.short_description = 'Сумма заказа'

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ['status']

    def __str__(self):
        return f'{self.firstname} {self.address}'


class ProductInOrder(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products_in_orders',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='products_in_orders'
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(
                1,
                message='too small number'
            ),
        ],
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    objects = ProductInOrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар и его количество в заказе'
        verbose_name_plural = 'товары и их количество в заказе'

    def __str__(self):
        return f'{self.product} {self.quantity}'


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
    )

    class Meta:
        verbose_name = 'расстояние'
        verbose_name_plural = 'расстояния'
        ordering = ['interval']

    def __str__(self):
        return f'{self.restaurant} - {self.interval}km'


def fetch_coordinates(apikey=settings.APIKEY, address=None):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


@receiver(post_save, sender=Order)
def change_status(sender, instance, **kwargs):
    if kwargs['update_fields']:
        for item in kwargs['update_fields']:
            if instance.restaurant and (item == 'restaurant'):
                instance.status = 2
                instance.save()
            elif item == 'address':
                restaurants = Restaurant.objects.all()
                for restaurant in restaurants:
                    try:
                        order_coordinates = fetch_coordinates(address=instance.address)
                        restaurant_coordinates = fetch_coordinates(address=restaurant.address)
                        interval = round(distance.distance(order_coordinates, restaurant_coordinates).km, 2)
                    except requests.exceptions:
                        interval = 'расстояние неизвестно'
                    Distance.objects.update_or_create(
                        order=instance,
                        restaurant=restaurant,
                        # interval=interval,
                        defaults={'interval': interval}
                    )
                if instance.status != 2:
                    instance.status = 1
                instance.save()
            else:
                if instance.status != 2:
                    instance.status = 1
                    instance.save()
