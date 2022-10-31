import requests
from django.conf import settings
from django.utils import timezone

from geolocation.models import Location

APIKEY = settings.YANDEX_GEOCODER_API_KEY


def fetch_coordinates(address, apikey=APIKEY):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()

    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lon, lat


def get_distance_with_units(distance):
    distance_with_units = f"{int(distance)} км"
    if distance < 10:
        distance_with_units = f"{distance:.2f} км"
    if distance < 1:
        distance_with_units = f"{int(distance*1000)} м"
    return distance_with_units


def get_or_create_location(address):
    try:
        location = Location.objects.get(address=address)
        return location.lon, location.lat
    except Location.DoesNotExist:
        coordinates = fetch_coordinates(address)
        if not coordinates:
            return
        lon, lat = coordinates
        Location.objects.create(
            address=address, lon=lon, lat=lat, updated_at=timezone.now()
        )
        return coordinates
