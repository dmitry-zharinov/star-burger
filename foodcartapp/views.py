import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.templatetags.static import static

from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
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
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


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
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    order = Order.objects.create(
        firstname=body['firstname'],
        lastname=body['lastname'],
        address=body['address'],
        phonenumber=body['phonenumber'],
    )
    for order_item in body['products']:
        try:
            product = Product.objects.get(id=order_item['product'])
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=order_item['quantity'],
            )
        except ObjectDoesNotExist:
            print("The product doesn't exist.")

    return JsonResponse({})
