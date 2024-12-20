# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

# DHT11 funktionalitet

from machine import Pin  # Importerer Pin-klassen til GPIO-styring
from time import sleep  # Importerer sleep-funktion
import dht  # Importerer bibliotek til DHT-sensorer

########################################
# CONFIGURATION
dht11_pin = 0  # Angiver GPIO for DHT11-sensoren

########################################
# OBJECT
dht11 = dht.DHT11(Pin(dht11_pin)) # Opretter et objekt for at kommunikere med sensoren

def get_temperature():
   """
   Læser temperaturen fra DHT11-sensoren.
   """
   dht11.measure()  # Gennemfører en måling ved at aktivere sensoren
   temp = dht11.temperature()  # Henter temperaturen fra sensoren
   return temp  # Returnerer temperaturen til den, der kalder funktionen
