import requests
from django.conf import settings
from geopy.distance import distance


APIKEY = settings.YANDEX_GEOCODER_API_KEY

def fetch_coordinates(address, apikey=APIKEY):
    base_url  = 'https://geocode-maps.yandex.ru/1.x'
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


def get_distance(address_from, address_to):
    coords_from = fetch_coordinates(address_from)
    coords_to = fetch_coordinates(address_to)
    return distance(coords_from, coords_to).km


def get_distance_with_units(distance):
    distance_with_units = f"{int(distance)} км"
    if distance < 10:
        distance_with_units = f"{distance:.2f} км"
    if distance < 1:
        distance_with_units = f"{int(distance*1000)} м"
    return distance_with_units