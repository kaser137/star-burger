from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from rest_framework.decorators import api_view

from .models import Product, Order, ProductInOrder


@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return Response([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    data = request.data
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    products = data['products']
    firstname = data['firstname']
    lastname = data['lastname']
    phonenumber = data['phonenumber']
    address = data['address']
    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
        address=address,
    )
    for food in products:
        serializer = ProductSerializer(data=food)
        serializer.is_valid(raise_exception=True)
        serializer = ProductInOrderSerializer(data=food)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.get(id=food['product'])
        quantity = food['quantity']
        ProductInOrder.objects.create(
            order=order,
            product=product,
            quantity=quantity,
        )
    return Response(data)


class ProductInOrderSerializer(ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = ['quantity']


class ProductSerializer(ModelSerializer):
    product = serializers.IntegerField(source='id')

    @staticmethod
    def validate_product(value):
        try:
            Product.objects.get(id=value)
        except ObjectDoesNotExist:
            raise ValidationError(f'Недопустимый первичный ключ: {value}')
        return value

    class Meta:
        model = Product
        fields = ['product']


class OrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'address', 'phonenumber', 'products']
