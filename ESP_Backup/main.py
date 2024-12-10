# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# Main

from uthingsboard.client import TBDeviceMqttClient
from time import sleep
from machine import reset, Pin
import gc
import secrets
from gps import gps, get_lat_lon
from lcd_funk import lcd, set_icon, write, clear
from dht11 import dht11, get_temperature
from battery_funk import initialize_potmeter, calculate_voltage, calculate_battery_voltage, calculate_battery_percentage

##################### OBJEKTER #####################

# client objekt til at forbinde til thingsboard
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token = secrets.ACCESS_TOKEN)
# Forbinder til ThingsBoard
client.connect()

############## TEST PRINT TIL SCHELL ##############

#####
# CONFIGURATION
PIN_POTMETER = 36  # GPIO-pin for potmeteret

# Kalibreringskonstanter for batterispænding
VOLTAGE_LOW = 1070
VOLTAGE_HIGH = 2430
a = (4.2 - 3.0) / (VOLTAGE_HIGH - VOLTAGE_LOW)
b = 3.0 - a * VOLTAGE_LOW

#####
# INITIALISATION
potmeter_adc = initialize_potmeter(PIN_POTMETER)
print("ADC and potmeter test\n")

print("Forbundet til thingsboard, sender og modtager data")

while True:
    
    try:
        
        if gc.mem_free() < 2000:          									# Frigør plads hvis der er under 2000 bytes tilbage
            gc.collect() 													# Frigør plads
        lat_lon = get_lat_lon()         								# retunere lat/lon i tuple format

        adc_val = potmeter_adc.read()
        uadc = calculate_voltage(adc_val)
        battery_voltage = calculate_battery_voltage(adc_val, a, b)
        battery_percentage = calculate_battery_percentage(battery_voltage)

        print(f"ADC Value: {adc_val}")
        print(f"Measured Voltage: {uadc:.2f} V")
        print(f"Battery Voltage: {battery_voltage:.2f} V")
        print(f"Battery Percentage: {battery_percentage:.2f}%\n")

        lcd.move_to(0,0)		
        lcd.putstr("\x00")
        write(0,2, int(battery_percentage), " %")
#         lcd_funk.lcd.move_to(0,8)
#         lcd_funk.lcd.putstr("\x01")
#         lcd_funk.write(0,9, float(gps.gps_dtc()), "")						# Viser retning (Nord, Syd, Øst, Vest) på LCD
        write(0,8, float(gps.get_course()), " C")    
        write(1,0, float(round(gps.get_speed(), 2)), " Km/t")	# Viser fart (Km/t) på LCD
        write(1,10, int(get_temperature()), "temp")
        write(2,0, (lat_lon[0]), " lat")
        write(3,0, (lat_lon[1]), " lon")
#        print(f"GPS-vinkel: {gps_course}° -> Retning: {retning}")
         
        if lat_lon:
                                                                              # Gemmer telemetry i dictionary      
            telemetry = {'latitude': lat_lon[0],
                          'longitude': lat_lon[1],
                          'speed':gps.get_speed(),
                          'course':gps.get_course(),
                          'temperature':get_temperature(),
                          'batteryLevel':battery_percentage}
            client.send_telemetry(telemetry) 						# Sender telemetry
        sleep(1)                           							# Send telemetry en gang i sekundet
    except KeyboardInterrupt:
        clear()
        client.disconnect()               							# Afbryder ThingsBoard
        print("STOOOOOOP")
        reset()                           							# reset ESP32
