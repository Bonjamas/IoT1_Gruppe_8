# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# Main

from uthingsboard.client import TBDeviceMqttClient
from time import sleep
from machine import reset, Pin
import gc
import secrets
import gps
import lcd_funk
import dht11

##################### OBJEKTER #####################

# client objekt til at forbinde til thingsboard
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)
# Forbinder til ThingsBoard
client.connect()

############## TEST PRINT TIL SCHELL ##############

print("Forbundet til thingsboard, sender og modtager data")

while True:
    try:
        if gc.mem_free() < 2000:          									# Frigør plads hvis der er under 2000 bytes tilbage
            gc.collect() 													# Frigør plads
        lat_lon = gps.get_lat_lon()         								# retunere lat/lon i tuple format
        
        lcd_funk.lcd.move_to(0,0)		
        lcd_funk.lcd.putstr("\x00")
#         lcd_funk.lcd.move_to(0,8)
#         lcd_funk.lcd.putstr("\x01")
#         lcd_funk.write(0,9, float(gps.gps_dtc()), "")						# Viser retning (Nord, Syd, Øst, Vest) på LCD
        lcd_funk.write(1,0, float(round(gps.gps.get_speed(), 2)), " Km/t")	# Viser fart (Km/t) på LCD
        lcd_funk.write(1,10, float(round(dht11.get_temperature(), 2)), "temp")
#         lcd_funk.write(2,0, float(lat_lon[0]), " lat") 						# Viser Latitude på LCD
#         lcd_funk.write(3,0, float(lat_lon[1]), " lon") 						# Viser Longitude på LCD
        lcd_funk.write(2,0, str(lat_lon[0]), " lat")
#         print(f"GPS-vinkel: {gps_course}° -> Retning: {retning}")
        
        if lat_lon:
                                                                             # Gemmer telemetry i dictionary      
            telemetry = {'latitude': lat_lon[0],
                         'longitude': lat_lon[1],
                         'speed':gps.gps.get_speed(),
                         'course':gps.gps.get_course(),
                         'temperature':dht11.get_temperature()}
            client.send_telemetry(telemetry) 						# Sender telemetry
        sleep(1)                           							# Send telemetry en gang i sekundet
    except KeyboardInterrupt:
        client.disconnect()               							# Afbryder ThingsBoard
        reset()                           							# reset ESP32
        