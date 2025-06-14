import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import socket
import json
from datetime import datetime

# === CARICAMENTO CONFIGURAZIONE ===
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

LAT = config["latitude"]
LON = config["longitude"]
PARAMS_TO_INCLUDE = config["parameters_to_include"]
MESSAGE_TEMPLATE = config["message_template"]
TARGET_IP = config["target_ip"]
TARGET_PORT = config["target_port"]
DST_CALLSIGN = config["dst_callsign"]

# === SETUP OPEN-METEO ===
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LAT,
    "longitude": LON,
    "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "wind_speed_10m", "wind_direction_10m"],
    "timezone": "auto",
    "forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]
current = response.Current()

# === MAPPING VARIABILI ===
data_map = {
    "temperature_2m": current.Variables(0).Value(),
    "relative_humidity_2m": current.Variables(1).Value(),
    "precipitation": current.Variables(2).Value(),
    "rain": current.Variables(3).Value(),
    "wind_speed_10m": current.Variables(4).Value(),
    "wind_direction_10m": current.Variables(5).Value()
}

# === FORMATTAZIONE MESSAGGIO ===
try:
    MESSAGE_TEXT = MESSAGE_TEMPLATE.format(**data_map)
except KeyError as e:
    print(f"Parametro mancante nel template: {e}")
    exit(1)

# === INVIO MESSAGGIO VIA UDP ===
def send_message():
    payload = {"type": "msg", "dst": DST_CALLSIGN, "msg": MESSAGE_TEXT}
    data = json.dumps(payload).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (TARGET_IP, TARGET_PORT))
    sock.close()
    current_dateTime = datetime.now()
    print(f"Inviato ({current_dateTime}): {MESSAGE_TEXT} -> {TARGET_IP}:{TARGET_PORT}")

# === ESECUZIONE ===
send_message()
