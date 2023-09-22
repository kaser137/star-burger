from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from star_burger import settings
from star_burger.functions import available_list
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem, Order, ProductInOrder


#
# def url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
#     """
#     Return ``True`` if the url uses an allowed host and a safe scheme.
#
#     Always return ``False`` on an empty url.
#
#     If ``require_https`` is ``True``, only 'https' will be considered a valid
#     scheme, as opposed to 'http' and 'https' with the default, ``False``.
#
#     Note: "True" doesn't entail that a URL is "safe". It may still be e.g.
#     quoted incorrectly. Ensure to also use django.utils.encoding.iri_to_uri()
#     on the path component of untrusted URLs.
#     """
#     if url is not None:
#         url = url.strip()
#     if not url:
#         return False
#     if allowed_hosts is None:
#         allowed_hosts = set()
#     elif isinstance(allowed_hosts, str):
#         allowed_hosts = {allowed_hosts}
#     # Chrome treats \ completely as / in paths but it could be part of some
#     # basic auth credentials so we need to check both URLs.
#     return (
#         _url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=require_https) and
#         _url_has_allowed_host_and_scheme(url.replace('\\', '/'), allowed_hosts, require_https=require_https)
#     )


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
        'id'
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url,
                           src=obj.image.url)

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductInOrder)
class ProductInOrderAdmin(admin.ModelAdmin):
    pass


class ProductInOrderInline(admin.TabularInline):
    model = ProductInOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'status',
        'firstname',
        'address',
        'phonenumber',
        'amount'
    ]

    readonly_fields = [
        'amount'
    ]
    inlines = [
        ProductInOrderInline,
    ]

    # def available_list(self, order_id):
    #     order = Order.objects.get(id=order_id)
    #     print(order)
    #
    #     products = [i.product for i in order.products_in_orders.all()]
    #     restaurants = []
    #     flag = 0
    #     print(products)
    #     for product in products:
    #         restaurants_for_product = RestaurantMenuItem.objects.filter(product=product).filter(availability=True).values_list(
    #             'restaurant__id', flat=True).distinct()
    #         if not flag:
    #             restaurants = restaurants_for_product
    #             print(product, '=============', restaurants_for_product)
    #             flag = 1
    #             continue
    #     restaurants = restaurants_for_product.intersection(restaurants)
    #     return list(restaurants)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        order_id = request.path.split('/')[-3]
        u = available_list(int(order_id))
        kwargs['queryset'] = Restaurant.objects.filter(id__in=u)
        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def response_change(self, request, obj):
        parent_redirect = super().response_post_save_change(request, obj)
        request_url = request.GET.get('next')
        if url_has_allowed_host_and_scheme(request_url, allowed_hosts=settings.ALLOWED_HOSTS):
            return redirect(request_url)
        return parent_redirect


# def available_list(order_id):
#     order = Order.objects.get(id=order_id)
#     products = [i.product for i in order.products_in_orders.all()]
#     restaurants = []
#     flag = 0
#     for product in products:
#         restaurants_for_product = RestaurantMenuItem.objects.filter(product=product).filter(
#             availability=True).values_list(
#             'restaurant__id', flat=True).distinct()
#         if not flag:
#             restaurants = restaurants_for_product
#             flag = 1
#             continue
#     restaurants = restaurants_for_product.intersection(restaurants)
#     return list(restaurants)
