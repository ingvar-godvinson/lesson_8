import json
import requests
import folium
import os
from dotenv import load_dotenv
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lat, lon = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat


def get_distance(coffee_shop):
    return coffee_shop["distance"]


def main():
    load_dotenv()
    apikey = os.getenv("APIKEY")

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_content = my_file.read()

    address = input("Где Вы находитесь? ")

    coffee_shops = json.loads(file_content)
    coords = fetch_coordinates(apikey, address)

    names = []
    for coffee_shop in coffee_shops:
        name = coffee_shop["Name"]
        lat = coffee_shop["Latitude_WGS84"]
        lon = coffee_shop["Longitude_WGS84"]
        dist = distance.distance((coords), (lat, lon)).km
        names.append(
            {"title": name, "distance": dist, "latitude": lat, "longitude": lon}
        )

    names.sort(key=get_distance)
    pages = names[:5]

    m = folium.Map(location=coords, zoom_start=15)
    folium.Marker(
        location=coords,
        popup=f"Ваше местоположение: {address}",
        tooltip=f"Вы здесь",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    for coffee_shop in pages:
        folium.Marker(
            location=[coffee_shop["latitude"], coffee_shop["longitude"]],
            popup=f'{coffee_shop["title"]} - {coffee_shop["distance"]:.2f} км',
            tooltip=coffee_shop["title"],
            icon=folium.Icon(color="blue", icon="coffee"),
        ).add_to(m)

    m.save("coffee_shop_map.html")


if __name__ == "__main__":
    main()
