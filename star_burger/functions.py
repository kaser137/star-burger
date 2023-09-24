import datetime
import requests
from geopy import distance
from django.db.models.signals import post_save
from django.dispatch import receiver

from foodcartapp.models import Order, RestaurantMenuItem, Restaurant
from restaurants_order_distances.models import Distance
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


def change_or_create_distance(order):
    restaurants = Restaurant.objects.all()
    for restaurant in restaurants:
        try:
            order_coordinates = fetch_coordinates(address=order.address)
            restaurant_coordinates = fetch_coordinates(address=restaurant.address)
            interval = round(distance.distance(order_coordinates, restaurant_coordinates).km, 2)
        except requests.exceptions:
            interval = None
        Distance.objects.update_or_create(
            order=order,
            restaurant=restaurant,
            defaults={'interval': interval, 'date': datetime.date.today()}

        )


@receiver(post_save, sender=Order)
def change_status(sender, instance, **kwargs):
    if kwargs['update_fields']:
        for item in kwargs['update_fields']:
            if instance.restaurant and (item == 'restaurant'):
                instance.status = 2
                instance.save()
            elif item == 'address':
                change_or_create_distance(instance)
                if instance.status != 2:
                    instance.status = 1
                instance.save()
            else:
                if instance.status != 2:
                    instance.status = 1
                    instance.save()
