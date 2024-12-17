# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

# DHT11 funktionalitet

from machine import Pin  # Importerer Pin-klassen til styring af hardware-pins
from time import sleep  # Importerer sleep-funktion til at pause eksekvering
import dht  # Importerer DHT-biblioteket til at arbejde med DHT-sensorer

########################################
# CONFIGURATION
dht11_pin = 0  # Pin-konfiguration for DHT11-sensoren (angiver, hvilken GPIO den er forbundet til)

########################################
# OBJECT
dht11 = dht.DHT11(Pin(dht11_pin))  
# Opretter en DHT11-objektinstans for at kommunikere med sensoren via den definerede pin

def get_temperature():
   """
   Læser temperaturen fra DHT11-sensoren.
   """
   dht11.measure()  # Gennemfører en måling ved at aktivere sensoren
   temp = dht11.temperature()  # Henter temperaturen fra sensoren
   return temp  # Returnerer temperaturen til den, der kalder funktionen
