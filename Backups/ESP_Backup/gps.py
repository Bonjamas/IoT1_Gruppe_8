# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# GPS funktionalitet

from machine import reset, UART, Pin
from gps_simple import GPS_SIMPLE

gps_port = 2                               	# ESP32 UART port, Educaboard ESP32 default UART port
gps_speed = 9600                           	# UART fart, default u-blox fart
uart = UART(gps_port, gps_speed)           	# UART object oprettes
gps = GPS_SIMPLE(uart)                     	# GPS object oprettes
# gps_course = gps.get_course()  				# Hent kursen via get_course
# retning = gps_dtc(gps_course)  				# Bestem retning baseret på kurs

def get_lat_lon():
    lat = lon = None                       	# Opret lat/lon variable med None som standard værdi 
    if gps.receive_nmea_data():            	# check om vi modtager data
                                            # check om dataen er gyldig
        if gps.get_latitude() != -999.0 and gps.get_longitude() != -999.0 and gps.get_validity() == "A":
            lat = str(gps.get_latitude())  	# gem latitude i lat variabel
            lon = str(gps.get_longitude()) 	# gem longitude i lon variabel
            return lat, lon                	# flere retur værdier, skal udpakkes ellers er de i tuple format
        else:                              	# hvis latitude og longitude er ugyldigt
            return False
    else:
        return False
    
# def gps_dtc(gps_vinkel):
# 
#     gps_vinkel = gps_vinkel % 360
# 
#     if (gps_vinkel >= 337.5 or gps_vinkel < 22.5):
#         return "Nord"
#     elif (22.5 <= gps_vinkel < 112.5):
#         return "Øst"
#     elif (112.5 <= gps_vinkel < 202.5):
#         return "Syd"
#     elif (202.5 <= gps_vinkel < 292.5):
#         return "Vest"
#     else:
#         return "Opdateres"  

    
    
