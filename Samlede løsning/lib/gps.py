# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

# GPS funktionalitet
from machine import reset, UART, Pin  # Importerer Pin-klasse, UART og reset-funktion
from gps_simple import GPS_SIMPLE  # Importerer biblioteket til at arbejde med GPS-data

# Konfiguration af GPS
gps_port = 2  # Angiver ESP32 UART-porten
gps_speed = 9600  # Angiver UART-baudrate

# Initialisering af UART og GPS
uart = UART(gps_port, gps_speed)  # Initialiserer UART med den angivne port og hastighed
gps = GPS_SIMPLE(uart)  # Opretter GPS-objekt

def get_lat_lon():
    """
    Henter GPS-koordinater (latitude og longitude) fra GPS'en.
    Returnerer en tuple med (lat, lon).
    """
    lat = lon = None  # Initialiserer latitude og longitude med None som standardværdi
    
    if gps.receive_nmea_data():  # Kontrollerer, om der modtages NMEA-data fra GPS'en
        if gps.get_validity() == "A":  # Kontrollerer, om data er gyldig ("A" for Active)
            lat = gps.get_latitude()  # Henter latitude og gemmer den i variablen lat
            lon = gps.get_longitude()  # Henter longitude og gemmer den i variablen lon
            return lat, lon  # Returnerer gyldige koordinater som en tuple
        elif gps.get_validity() == "V":  # Kontrollerer, om data er ugyldig ("V" for Void)
            lat = gps.get_latitude()  # Henter latitude (selvom data er ugyldig)
            lon = gps.get_longitude()  # Henter longitude (selvom data er ugyldig)
            return lat, lon  # Returnerer de ugyldige koordinater som en tuple
    else:
        # Hvis der ikke modtages data, returneres standardkoordinater
        lat = 0.00000
        lon = 0.00000
        return lat, lon  # Returnerer nulkoordinater som en tuple