# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

from machine import Pin, I2C  # Importerer hardwareklasser til GPIO-styring og I2C-kommunikation
from time import sleep, ticks_ms  # Importerer tidsfunktioner, inkl. millisekund-tæller
from uthingsboard.client import TBDeviceMqttClient  # Importerer MQTT-klienten til ThingsBoard
import gc  # Garbage collector til hukommelsesstyring
import secrets  # Indeholder fortrolige oplysninger som serveradresse, adgangstoken & WIFI
from alarm_laas_lys import set_brake_light, check_brake, np_clear, alarm, control_solenoid  # Importerer funktionerne alarm, lås og Neopixel
from gps import gps, get_lat_lon  # Importere egne funktioner til GPS-modul
from lcd import lcd, set_icon, write, clear  # Importere LCD-styring
from dht11 import get_temperature  # Temperaturmåling fra DHT11-sensoren
from ina219_lib import INA219  # Strømmåling via INA219-sensor
from mpu6050 import MPU6050  # Bevægelsessensor / Gyroskop
import sys  # Til systemkommandoer som at afslutte programmet

# Global variables
alarm_enabled = False  # Styrer alarmens aktivering/deaktivering
solenoid_enabled = False  # Styrer solenoidens aktivering/deaktivering

# Initialization
i2c = I2C(0)  # Initialiserer I2C-kommunikation på standard SDA/SCL pins
imu = MPU6050(i2c)  # Initialiserer MPU6050 bevægelsessensor
ina = INA219(i2c)  # Initialiserer INA219 strøm- og spændingssensor

# ThingsBoard MQTT client
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)  # Forbinder til ThingsBoard med adgangstoken

# RPC Handler
def handler(req_id, method, params):
    """
    Håndterer fjernprocedurens kald (RPC) forespørgsler fra ThingsBoard-platformen.
    
    - req_id: Unikt ID for forespørgslen, bruges til at identificere svaret på serveren.
    - method: Navn på metoden, der skal kaldes, som f.eks. 'toggle_alarm' eller 'toggle_solenoid'.
    - params: De parametre, der følger med RPC-kaldet. Typisk en værdi, der angiver, hvad der skal ske.
    """
    global alarm_enabled, solenoid_enabled  # Globale variabler, der styrer alarm og solenoid

    try:
        # Tjekker, hvilken metode der kaldes, og udfører handlinger baseret på det.
        if method == "toggle_alarm":  # Hvis serveren beder om at aktivere/deaktivere alarmen
            alarm_enabled = bool(int(params))  # Konverterer parameteren til en boolsk værdi
            # Parametret forventes at være '0' eller '1', som konverteres til False eller True.
            if alarm_enabled:
                # Alarm aktiveres
                print("Alarm activated")  # Udskriver status for debugging
                lcd.clear()  # Rydder LCD-skærmen for at undgå forstyrrende visninger
            else:
                # Alarm deaktiveres
                print("Alarm deactivated")  # Udskriver status for debugging
                np_clear()  # Slukker Neopixel

        elif method == "toggle_solenoid":  # Hvis serveren beder om at styre solenoiden
            solenoid_enabled = bool(int(params))  # Konverterer parameteren til en boolsk værdi
            # Parametret forventes at være '0' (slukket) eller '1' (tændt).
            control_solenoid(solenoid_enabled)  # Styrer solenoidens fysiske tilstand (åben/lukket)
            
            # Synkroniserer alarmens status med solenoiden
            # Når solenoiden aktiveres, sættes alarmen automatisk til samme status.
            alarm_enabled = solenoid_enabled  
            
            lcd.clear()  # Rydder LCD for at forhindre uønskede data fra tidligere handlinger
            # Udskriver tilstanden af solenoiden for debugging:
            print(f"Solenoid {'activated' if solenoid_enabled else 'deactivated'}")
            
            if not solenoid_enabled:
                # Hvis solenoiden er slukket, ryddes Neopixel
                np_clear()

    except Exception as e:  # Fanger fejl, der kan opstå under håndtering af RPC
        # Udskriver en fejlmeddelelse.
        print(f"Error in RPC handler: {e}")

# Connect to ThingsBoard
client.connect()  # Forbinder til ThingsBoard-serveren
client.set_server_side_rpc_request_handler(handler)  # Sætter RPC-handleren
print("Connected to ThingsBoard")

start = ticks_ms()  # Starter tidstælleren
check_movement = True  # Variabel til overvågning af bevægelse
send_data = True  # Variabel til kontrol af datatelemetri

while True:  # Uendelig løkke til at overvåge sensorer og sende data
    try:
        # Læsning af sensordata
        imu_data = imu.get_values()  # Henter accelerometerdata fra MPU6050
        client.check_msg()  # Tjekker for indkommende MQTT-beskeder fra ThingsBoard

        ### Bevægelsesanalyse (baseret på accelerometerets y-akse) ###
        if -500 < imu_data.get("acceleration y") < 500 and check_movement:
            # Hvis accelerationen på y-aksen er inden for et stille interval, starter en timer
            timer = ticks_ms()  # Registrerer starttidspunkt for stilstand
            check_movement = False  # Marker, at der ikke er bevægelse
        if abs(imu_data.get("acceleration y")) > 500 and not check_movement:
            # Hvis y-aksens acceleration overstiger tærsklen, marker bevægelse igen
            check_movement = True
            send_data = True  # Tillader, at data sendes igen
        if not check_movement and ticks_ms() - timer > 180000:
            # Hvis der ikke har været bevægelse i over 3 minutter (180.000 ms):
            send_data = False  # Stop med at sende data
            np_clear()  # Slukker Neopixel
            lcd.clear()  # Ryd displayet

        ### Behandling af data, hvis bevægelse er registreret ###
        if send_data:
            # Hvis alarm eller solenoid er aktiveret, tjek for kritiske hændelser
            if alarm_enabled or solenoid_enabled:
                if imu_data.get("acceleration x") < -5000:
                    # Hvis x-aksens acceleration overstiger -5000, aktiver alarmen
                    alarm()
                else:
                    # Hvis x-aksens acceleration ikke overstiger -5000, sluk Neopixel
                    np_clear()
            else:
                # Hvis hverken alarm eller solenoid er aktiveret, tjek for bremseaktivitet
                check_brake(imu, alarm_enabled)

            # Opdatering af sensordata og display hvert 5. sekund
            if ticks_ms() - start > 5000:
                if not alarm_enabled:  # Kun opdater, hvis alarmen ikke er aktiv
                    # Hent strøm og spændingsdata fra INA219-sensoren
                    current = ina.get_current()  # Måler den aktuelle strøm
                    voltage = ina.get_bus_voltage()  # Måler spændingen
                    # Beregn batteriniveau i procent baseret på spændingsintervallet (6V - 8.4V)
                    battery_percent = max(0, min(100, ((voltage - 6) / (8.4 - 6)) * 100))
                    # Estimér den resterende batteritid i timer
                    remaining_time = (((battery_percent / 100) * 1800) / current)

                    # Hent GPS-data (latitude og longitude). Hvis GPS-data ikke er tilgængelig, returneres (0, 0).
                    lat_lon = get_lat_lon() or (0, 0)

                    ### Viser data på LCD-skærmen ###
                    lcd.move_to(0, 0)  # Flytter cursor til startposition
                    lcd.putstr("\x00")  # Viser et batteri ikon
                    write(0, 1, int(battery_percent), "%")  # Skriver batteriprocent
                    write(0, 5, int(remaining_time), "h")  # Skriver estimeret batteritid
                    write(0, 10, gps.get_course(), "C")  # Skriver kurs (retning)
                    write(1, 0, round(gps.get_speed(), 2), " Km/t")  # Skriver hastighed i km/t
                    write(1, 10, int(get_temperature()), " temp")  # Skriver temperatur
                    write(2, 0, lat_lon[0], " lat")  # Skriver latitude
                    write(3, 0, lat_lon[1], " lon")  # Skriver longitude

                    ### Sender data som telemetri til ThingsBoard ###
                    telemetry = {
                        'latitude': lat_lon[0],
                        'longitude': lat_lon[1],
                        'speed': gps.get_speed(),
                        'course': gps.get_course(),
                        'temperature': get_temperature(),
                        'batteryLevel': battery_percent,
                        'capacity': remaining_time,
                    }
                    client.send_telemetry(telemetry)  # Sender data til serveren
                start = ticks_ms()  # Opdaterer starttidspunktet for næste cyklus

            ### Hukommelsesoptimering ###
            if ticks_ms() - start > 10000 and gc.mem_free() < 2000:
                # Hvis der er gået over 10 sekunder, og der er mindre end 2 KB ledig hukommelse
                gc.collect()  # Frigør hukommelse ved hjælp af garbage collection

    except Exception as e:
        # Håndtering af fejl, der kan opstå i løkken
        print(e)  # Udskriver fejlmeddelelse til debugging

    except KeyboardInterrupt:  # Afslutter programmet ved Ctrl+C
        print("Exiting program...")
        client.disconnect()
        np_clear() # Slukker Neopixel
        lcd.clear() # Ryd displayet
        sys.exit() # Stopper Kode