from machine import Pin
import requests
import secrets

ledRed = Pin(26, Pin.OUT)
ledGreen = Pin(13, Pin.OUT)
relay = Pin(17, Pin.OUT)

# greenPower = fetch_CO2Emis()

def relayOnOff(onoff):
    relay.value(onoff)
    return None

def fetch_CO2Emis():
    emis = requests.get(
        url = "https://api.energidataservice.dk/dataset/CO2Emis?limit=5")

    APIco2 = emis.json().get('records')[1].get('CO2Emission')
    #print("CO2 g pr. kwh : " ,APIco2)
    return APIco2

while True:
    greenPower = fetch_CO2Emis()
    if greenPower < 50:
        print("Der er grøn strøm", greenPower, " CO2/kwh")
        ledGreen.on()
        relayOnOff(1)
    elif greenPower > 50:
        print("Der er ikke grøn strøm:", greenPower , " CO2/kwh")
        ledRed.on()
        relayOnOff(0)
            
            
            
        
        
