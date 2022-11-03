from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy.distance import distance

from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem
from geolocation.geolocation import (get_distance_with_units,
                                     get_or_create_locations)


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability
                        for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False)
                                for restaurant in restaurants]

        products_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_restaurant_availability': products_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.filter(status='NEW').fetch_with_price()
    restaurant_menu_items = RestaurantMenuItem.objects.all().select_related(
        'restaurant', 'product'
    )

    order_addresses = [order.address for order in orders]
    restaurant_addresses = [
        restaurant.address for restaurant in Restaurant.objects.all()
    ]
    locations = get_or_create_locations(
        *order_addresses, *restaurant_addresses
    )

    order_restaurants = []
    for order in orders:
        for order_product in order.items.all():
            product_rests = set([
                menu_item.restaurant for menu_item in restaurant_menu_items
                if order_product.product == menu_item.product
                and menu_item.availability
            ])
            order_restaurants.append(product_rests)
        order_location = locations.get(order.address, None)
        suitable_restaurants = set.intersection(*order_restaurants)
        for restaurant in suitable_restaurants:
            restaurant_location = locations.get(restaurant.address, None)
            restaurant.distance = distance(
                order_location, restaurant_location
            ).km
            restaurant.distance_text = get_distance_with_units(
                restaurant.distance
            )
        suitable_restaurants = sorted(
            suitable_restaurants,
            key=lambda restaurant: restaurant.distance
        )
        order.suitable_restaurants = suitable_restaurants

    return render(request, template_name='order_items.html', context={
        'orders': orders,
    })
