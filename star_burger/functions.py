from foodcartapp.models import Order, RestaurantMenuItem


def available_list(order_id):
    order = Order.objects.get(id=order_id)
    products = [i.product for i in order.products_in_orders.all()]
    restaurants = []
    flag = 0
    for product in products:
        restaurants_for_product = RestaurantMenuItem.objects.filter(product=product).filter(
            availability=True).values_list(
            'restaurant__id', flat=True).distinct()
        if not flag:
            restaurants = restaurants_for_product
            flag = 1
            continue
    restaurants = restaurants_for_product.intersection(restaurants)
    return list(restaurants)
