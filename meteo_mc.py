import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os
import socket
import json
from datetime import datetime

# Parte di questo codice è stato generato da Open-Meteo
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

# INSERISCI LA TUA LATITUDINE E LONGITUDINE
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 43.7792,
	"longitude": 11.2463,
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "wind_speed_10m", "wind_direction_10m"],
	"timezone": "auto",
	"forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_precipitation = current.Variables(2).Value()
current_rain = current.Variables(3).Value()
current_wind_speed_10m = current.Variables(4).Value()
current_wind_direction_10m = current.Variables(5).Value()
print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
print(f"Current precipitation {current_precipitation}")
print(f"Current rain {current_rain}")
print(f"Current wind_speed_10m {current_wind_speed_10m}")
print(f"Current wind_direction_10m {current_wind_direction_10m}")

# per rete meshcom via seriale
# root@debian-sviluppo:~# stty -F /dev/ttyACM0 115200 raw -echo
# root@debian-sviluppo:~# echo ":{222} test" > /dev/ttyACM0

# MODIFICARE A PROPRIO USO IL MESSAGGIO
messaggio = f"Firenze - Temp: {round(current.Variables(0).Value(),1)}C Umid: {current_relative_humidity_2m}% Pioggia: {round(current_precipitation,2)}mm Vento: {round(current_wind_speed_10m)}Km/h"
#os.system ('stty -F /dev/ttyACM0 115200')
#os.system ('stty -F /dev/ttyACM0 speed')
#os.system('echo ":{22251}' + messaggio + '" > /dev/ttyACM0')

# CONFIGURAZIONE
TARGET_IP = "1.2.3.4"             # Sostituire con l'IP di destinazione
TARGET_PORT = 1799                # Porta di destinazione
DST_CALLSIGN = "22251"            # Destinatario del messaggio (o gruppo)
MESSAGE_TEXT = messaggio          # Contenuto del messaggio

# Creazione del socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_message():
    payload = {"type": "msg", "dst": DST_CALLSIGN, "msg": MESSAGE_TEXT} # formattato per la rete MC
    data = json.dumps(payload).encode()
    sock.sendto(data, (TARGET_IP, TARGET_PORT))
    current_dateTime = datetime.now()
    print(f"Inviato ({current_dateTime}): {data} -> {TARGET_IP}:{TARGET_PORT}")

# Invio del messaggio
send_message()
# Chiusura del socket
sock.close()
