#!/usr/bin/env python3

import requests
import socket
import json
from datetime import datetime

# -------------------------------------------------
# CONFIGURAZIONE WEATHER.COM / WUNDERGROUND
# -------------------------------------------------

WEATHER_API_KEY = "APIKEY"            # <-- API KEY Weather Underground
STATION_ID = "IDSTAZIONE"             # <-- ID stazione PWS
UNITS = "m"                           # m = metriche

WEATHER_URL = "https://api.weather.com/v2/pws/observations/current"

# API Call example
# https://api.weather.com/v2/pws/observations/current?stationId=IDSTAZIONE&format=json&units=m&apiKey=APIKEY

# Mappatura campi JSON (configurabile)
JSON_FIELDS = {
    "temperature": ("metric", "temp"),
    "humidity": "humidity",
    "wind_speed": ("metric", "windSpeed"),
    "wind_dir": "winddir",
    "precip_rate": ("metric", "precipRate"),
    "precip_total": ("metric", "precipTotal"),
    "pressure": ("metric", "pressure")
}

LOCATION_NAME = "YOUR Meteo station QTH"

# -------------------------------------------------
# CONFIGURAZIONE MESHCOM LORA CARD
# -------------------------------------------------

TARGET_IP = "1.2.3.4"
TARGET_PORT = 1799
DST_CALLSIGN = "22299" # Meshcom group to send meteo messages to

# -------------------------------------------------
# FUNZIONI
# -------------------------------------------------

def get_weather_data():
    params = {
        "stationId": STATION_ID,
        "format": "json",
        "units": UNITS,
        "apiKey": WEATHER_API_KEY
    }

    response = requests.get(WEATHER_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_field(obs, field):
    """Gestisce campi annidati o semplici"""
    if isinstance(field, tuple):
        return obs.get(field[0], {}).get(field[1])
    return obs.get(field)


def build_message(obs):
    temp = extract_field(obs, JSON_FIELDS["temperature"])
    hum  = extract_field(obs, JSON_FIELDS["humidity"])
    wind = extract_field(obs, JSON_FIELDS["wind_speed"])
    rain = extract_field(obs, JSON_FIELDS["precip_rate"])
    rtot = extract_field(obs, JSON_FIELDS["precip_total"])
    pres = extract_field(obs, JSON_FIELDS["pressure"])
    
    msg = (
        f"{LOCATION_NAME} - "
        f"Temp: {temp}C "
        f"Umid: {hum}% "
        f"Pioggia: {rain}mm "
        f"Da mezzanotte: {rtot}mm "
        f"Vento: {wind}Km/h "
        f"Pressione: {pres}mb"
    )

    return msg


def send_message(message):
    payload = {
        "type": "msg",
        "dst": DST_CALLSIGN,
        "msg": message
    }

    data = json.dumps(payload).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (TARGET_IP, TARGET_PORT))
    sock.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Inviato ({now}): {data} -> {TARGET_IP}:{TARGET_PORT}")


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    weather_json = get_weather_data()
    obs = weather_json["observations"][0]

    message = build_message(obs)
    print("Messaggio:", message)

    send_message(message)


if __name__ == "__main__":
    main()
