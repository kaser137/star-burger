from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from rest_framework.decorators import api_view
from django.db import transaction

from foodcartapp.functions import change_or_create_distance
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
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


class ProductSerializer(ModelSerializer):
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


class ProductInOrderSerializer(ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ProductInOrderSerializer(many=True, allow_empty=False, write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
        )
        change_or_create_distance(order)
        products_in_order = [
            ProductInOrder(
                order=order,
                product=food['product'],
                price=food['product'].price,
                quantity=food['quantity']
            )
            for food in validated_data['products']
        ]
        ProductInOrder.objects.bulk_create(products_in_order)
        return order

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']
