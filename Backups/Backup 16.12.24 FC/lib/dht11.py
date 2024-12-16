# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# DHT11 funktionalitet

from machine import Pin
from time import sleep
import dht

########################################
# CONFIGURATION
dht11_pin = 0

########################################
# OBJECT
dht11 = dht.DHT11(Pin(dht11_pin))

def get_temperature():
   dht11.measure()				#Make the measurement
   temp = dht11.temperature()	#Get the temperature
   return temp