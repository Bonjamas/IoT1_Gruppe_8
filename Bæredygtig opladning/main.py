# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# ID: 8 --- Kategori: Grøn opladning --- Prioritet: 2
# Krav: Løsningen skal være bæredygtigt og opladning af løsningens batteri skal lades med grøn energi.
# Der skal indikeres på løsningen når der er grøn energi til rådighed på elnettet, og hvornår der ikke
# er grøn energi til rådighed. Løsningen skal tænde for laderen når der er grøn energi og slukke når det
# ikke er grøn energi til rådighed.

from machine import Pin
import requests
import secrets
from time import sleep

################ PINS ################
ledRed = Pin(26, Pin.OUT)
ledGreen = Pin(13, Pin.OUT)
relay = Pin(17, Pin.OUT)

########### FUNKTIONER ###########

# Håndtere om relæet er tændt eller slukket, value 1-0
def relayOnOff(onoff):
    relay.value(onoff)
    return None

# Håndtere API kaldet til energidataservice.dk, den henter CO2 pr kwh
def fetch_CO2Emis():
    emis = requests.get(
        url = "https://api.energidataservice.dk/dataset/CO2Emis?limit=5")

    APIco2 = emis.json().get('records')[1].get('CO2Emission')
    #print("CO2 g pr. kwh : " ,APIco2)
    return APIco2

while True:
    greenPower = fetch_CO2Emis()
    if greenPower < 50:											#Hvis der er under 50g CO2 pr kwh starter opladningen
        print("Der er grøn strøm", greenPower, " CO2/kwh")
        ledGreen.on()											#Tænder grøn LED 
        relayOnOff(1)											#Tænder relæet
    elif greenPower > 50:										#Hvis der er over 50g CO2 pr kwh starter opladningen IKKE
        print("Der er ikke grøn strøm:", greenPower , " CO2/kwh")
        ledRed.on()
        relayOnOff(0)
        
    sleep(30)
            
            
            
        
        
