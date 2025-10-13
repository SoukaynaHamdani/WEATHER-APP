import requests
from datetime import date

def geocode_location(location):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    r = requests.get(url)
    if r.status_code != 200 or not r.json().get("results"):
        return None
    res = r.json()["results"][0]
    return {
        "name": res["name"],
        "latitude": res["latitude"],
        "longitude": res["longitude"],
        "country": res.get("country", "")
    }

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json().get("current_weather")
    return data

def get_forecast(lat, lon, date_from, date_to):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={date_from}&end_date={date_to}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json().get('daily')

def google_map_url(lat, lon, location):
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

def youtube_search_url(location):
    loc = location.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={loc}+weather"
