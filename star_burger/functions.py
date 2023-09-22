import requests

from foodcartapp.models import Order, RestaurantMenuItem
from star_burger import settings


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
