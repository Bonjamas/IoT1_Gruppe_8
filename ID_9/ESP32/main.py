from time import sleep, time
from machine import UART, Pin
from gps_simple import GPS_SIMPLE
from uthingsboard.client import TBDeviceMqttClient
import secrets

# GPS funktionalitet

gps_port = 2
gps_speed = 9600
uart = UART(gps_port, gps_speed)
gps = GPS_SIMPLE(uart)

# ThingsBoard klient
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)
client.connect()
print("Forbundet til ThingsBoard")

def get_lat_lon():
    """Henter GPS-koordinater"""
    if gps.receive_nmea_data():
        if gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            return gps.get_latitude(), gps.get_longitude()
    return None, None

def send_to_thingsboard(lat, lon):
    """Sender GPS-koordinater til ThingsBoard"""
    telemetry = {
        "latitude": lat,
        "longitude": lon
    }
    client.send_telemetry(telemetry)
    print(f"Sendt til ThingsBoard: {telemetry}")

def monitor_bike():
    """Overvåger cyklens status"""
    last_movement_time = time()
    stationary_time = 180  # 3 minutter

    while True:
        lat, lon = get_lat_lon()

        if lat is not None and lon is not None:
            current_time = time()
            print(f"GPS position: Latitude {lat}, Longitude {lon}")

            # Hvis cyklen har stået stille længe nok og nu er i bevægelse
            if current_time - last_movement_time > stationary_time:
                print("Cyklen har været stationær i mere end 3 minutter.")
                send_to_thingsboard(lat, lon)

            # Registrer bevægelse og nulstil tæller
            if gps.get_speed() > 0:
                print("Bevægelse detekteret.")
                last_movement_time = current_time

        sleep(1)

try:
    monitor_bike()
except KeyboardInterrupt:
    print("Afslutter...")
    client.disconnect()