import phonenumbers
from rest_framework import status
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
    try:
        products = data['products']
    except KeyError:
        return Response(
            {'error': 'products key is not presented'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        first_name = data['firstname']
    except KeyError:
        return Response(
            {'error': 'firstname key is not presented'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        last_name = data['lastname']
    except KeyError:
        return Response(
            {'error': 'lastname key is not presented'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        phone = data['phonenumber']
    except KeyError:
        return Response(
            {'error': 'phonenumber key is not presented'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        address = data['address']
    except KeyError:
        return Response(
            {'error': 'address key is not presented'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    phone = phonenumbers.parse(phone, 'RU')
    if not isinstance(products, list) or not products:
        return Response(
            {'error': 'products key is not specified, or not list'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(first_name, str) or not first_name:
        return Response(
            {'error': 'firstname key is not specified, or not str'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(last_name, str) or not last_name:
        return Response(
            {'error': 'lastname key is not specified, or not str'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not phonenumbers.is_valid_number(phone):
        return Response(
            {'error': 'phonenumber key is not valid'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(address, str) or not address:
        return Response(
            {'error': 'address key is not specified, or not str'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order = Order.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        address=address,
    )
    for food in products:
        try:
            product = Product.objects.get(id=food['product'])
        except ObjectDoesNotExist:
            order.delete()
            return Response(
                {'error': f'product with id = {food["product"]} does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        quantity = food['quantity']
        ProductInOrder.objects.create(
            order=order,
            product=product,
            quantity=quantity,
        )
    return Response(data)
