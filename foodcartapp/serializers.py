from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError
from foodcartapp.functions import change_or_create_distance
from foodcartapp.models import Product, ProductInOrder, Order


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
