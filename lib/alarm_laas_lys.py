# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

from time import sleep  # Importerer sleep-funktion
from machine import Pin, PWM  # Importerer funktioner til GPIO-styring og PWM
from neopixel import NeoPixel  # Importerer NeoPixel-bibliotek
from mpu6050 import MPU6050  # Importerer bibliotek til MPU6050-sensor

# Konstanter
NUM_PIXELS = 12  # Antal NeoPixels i ringen
NEOPIXEL_PIN = 12  # Pin til NeoPixel
BUZZER_PIN = 26  # Pin til buzzer
SOLENOID_PIN = 14  # Pin til solenoid actuator

# Initialisering
buzzer = PWM(Pin(BUZZER_PIN, Pin.OUT), duty=0)  # Opretter PWM-objekt til buzzer, initialiseret med duty=0 (slukket)
np = NeoPixel(Pin(NEOPIXEL_PIN, Pin.OUT), NUM_PIXELS)  # Initialiserer NeoPixel
solenoid = Pin(SOLENOID_PIN, Pin.OUT)  # Initialiserer solenoid

def set_color(r, g, b):
    """Sætter alle NeoPixels til en bestemt farve."""
    for i in range(NUM_PIXELS):  # Gennemgår alle pixels
        np[i] = (r, g, b)  # Sætter farve på pixel
    np.write()  # Sender data til NeoPixel-ringen

def np_clear():
    """Slukker alle NeoPixels."""
    for i in range(NUM_PIXELS):  # Gennemgår alle pixels
        np[i] = (0, 0, 0)  # Sætter farven til sort (slukker)
    np.write()  # Opdaterer NeoPixel-ringen

def alarm():
    """Afspiller en alarm med lys og lyd."""
    for i in range(5):  # Gentager alarmsekvensen 5 gange
        set_color(255, 0, 0)  # Tænd rødt lys
        buzzer.duty(512)  # Sætter buzzerens duty-cycle til 50% (aktiveret)
        buzzer.freq(440)  # Indstiller buzzerens frekvens til 440 Hz (lav tone)
        sleep(0.5)  # Pause i 0.5 sekunder

        np_clear()  # Sluk lyset
        buzzer.duty(512)  # Beholder duty-cycle
        buzzer.freq(1012)  # Indstiller frekvens til 1012 Hz (høj tone)
        sleep(0.5)  # Pause i 0.5 sekunder

    # Sluk alarmen
    np_clear()  # Slukker NeoPixels
    buzzer.duty(0)  # Slukker buzzer

def brake_light(imu, alarm_enabled):
    """Kontrollerer bremselyset baseret på accelerationsdata."""
    if not alarm_enabled:  # Kun tænd bremselys, hvis alarm ikke er aktiveret
        imu_data = imu.get_values()  # Henter accelerometerdata fra MPU6050
        ay = imu_data["acceleration y"]  # Læser acceleration langs y-aksen

        if ay > 1000:  # Tærskel for bremsning
            for i in range(3):
                set_color(255, 0, 0)
                sleep(0.2)
                np_clear()
                sleep(0.2)
        else:
            set_color(255, 0, 0)  # Holder bremselyset tændt
                
    else:
        np_clear()  # Slukker NeoPixels, hvis alarm er aktiveret

def control_solenoid():
    """Styrer solenoid actuator med en aktiveringsperiode."""
    solenoid.value(1)  # Aktiverer solenoiden
    sleep(3)  # Hold solenoiden aktiveret i 3 sekunder
    solenoid.value(0)  # Deaktiverer solenoiden
