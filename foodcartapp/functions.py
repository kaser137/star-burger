import requests
from geopy import distance
from django.db.models.signals import post_save
from django.dispatch import receiver
from foodcartapp.models import Order, RestaurantMenuItem, Restaurant
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


def sort_key(string):
    return string.split(' ')[-2]


def get_interval(restaurant, order):
    if restaurant.lat and restaurant.lon and order.lat and order.lon:
        return round(distance.distance((restaurant.lat, restaurant.lon), (order.lat, order.lon)).km, 2)
    else:
        return None


def get_coordinates(instance):
    try:
        coordinates = fetch_coordinates(address=instance.address)
        if coordinates:
            instance.lat, instance.lon = coordinates
        else:
            instance.lat, instance.lon = None, None
    except requests.RequestException:
        instance.lat, instance.lon = None, None
    instance.save()


@receiver(post_save, sender=Restaurant)
def change_restaurant_address(sender, instance, created, **kwargs):
    if created:
        get_coordinates(instance)
    if kwargs['update_fields']:
        address = kwargs['update_fields'].get('address')
        if address:
            get_coordinates(instance)


@receiver(post_save, sender=Order)
def change_status(sender, instance, created, **kwargs):
    if created:
        get_coordinates(instance)
    if kwargs['update_fields']:
        for item in kwargs['update_fields']:
            if instance.restaurant and (item == 'restaurant'):
                instance.status = 2
                instance.save()
            elif item == 'address':
                if instance.status != 2:
                    instance.status = 1
                get_coordinates(instance)
            else:
                if instance.status != 2:
                    instance.status = 1
                    instance.save()
