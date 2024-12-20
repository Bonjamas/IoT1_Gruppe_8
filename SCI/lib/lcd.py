# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

# LCD funktionalitet

from machine import Pin, PWM  # Importerer PWM og Pin-klasse
from time import sleep  # Importerer sleep
from gpio_lcd import GpioLcd  # Importerer LCD-bibliotek

# Instans af LCD-objekt
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),  # Initialiserer LCD med de nødvendige pins
              d4_pin=Pin(33), d5_pin=Pin(32),     
              d6_pin=Pin(21), d7_pin=Pin(22),    
              num_lines=4, num_columns=20)        # Konfigurerer skærmen til 4 linjer og 20 kolonner

# Funktion til at oprette og gemme ikoner på LCD-skærmen
def set_icon(lcd, location, char_map):
    """
    Gemmer et brugerdefineret ikon på LCD-skærmen.
    - location: Plads (0-7) hvor ikonet skal gemmes
    - char_map: Pixeldata for ikonet
    """
    location &= 0x07  # Sikrer, at placeringen er mellem 0 og 7
    lcd.custom_char(location, bytearray(char_map))

# Ikondata til et batteriikon
battery_icon = [0b00000,
                0b01110,
                0b11111,
                0b10001,
                0b10011,
                0b10111,
                0b11111,
                0b11111]

# Gemmer batteriikonet på plads 0
set_icon(lcd, 0, battery_icon)

# Funktion til at skrive tekst til LCD-skærmen
def write(linje, kolonne, tekst, ikon=" "):
    """
    Skriver tekst til en bestemt position på LCD-skærmen.
    - linje: Linjenummer (0-indekseret)
    - kolonne: Kolonnenummer (0-indekseret)
    - tekst: Teksten der skal skrives
    - ikon: Valgfrit ikon der vises efter teksten
    """
    lcd.move_to(kolonne, linje)  # Flytter cursoren til den specificerede position
    lcd.putstr(str(tekst) + ikon + " ")  # Skriver teksten og ikonet

# Funktion til at rydde LCD-skærmen
def clear():
    """
    Rydder LCD-skærmen for al tekst og ikoner.
    """
    lcd.clear()