from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
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
        if isinstance(products, list) and products:
            first_name = data['firstname']
            last_name = data['lastname']
            phone = data['phonenumber']
            address = data['address']
            order = Order.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
            )
            for food in products:
                product = Product.objects.get(id=food['product'])
                quantity = food['quantity']
                ProductInOrder.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )
            return Response(data)
    except KeyError:
        pass
    return Response(
        {'error': 'products key is not presented, or is None, or not list'},
        status=status.HTTP_400_BAD_REQUEST,
    )
