from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum


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
    status = models.CharField(
        'статус',
        max_length=2,
        choices=STATUS,
        default=0,
        db_index=True
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

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.address}'


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1, message='too small number')]
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
