
import phonenumbers
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumbers import PhoneNumberFormat, is_valid_number
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError

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


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True,
                                   allow_null=False,
                                   write_only=True)

    class Meta:
        model = Order
        fields = ['products',
                  'id',
                  'firstname',
                  'lastname',
                  'phonenumber',
                  'address']

    def validate_products(self, value):
        if not value:
            raise ValidationError('Этот список не может быть пустым.')
        return value

    def validate_phonenumber(self, value):
        parsed_phone = phonenumbers.parse(value, "RU")
        if not is_valid_number(parsed_phone):
            raise ValidationError('Введен некорректный номер телефона.')

        standardized_phone = phonenumbers.format_number(
            parsed_phone, PhoneNumberFormat.E164
        )
        return standardized_phone


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        address=serializer.validated_data['address'],
        phonenumber=serializer.validated_data['phonenumber'],
    )

    order_items_fields = serializer.validated_data['products']
    order_items = [
        OrderItem(order=order, price=fields['product'].price, **fields)
        for fields in order_items_fields
    ]
    OrderItem.objects.bulk_create(order_items)
    response_data = serializer.data
    response_data['id'] = order.id
    return Response(response_data)
