# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen & Benjamin Landling Pedersen
# Mere info www.gruppe8.dk

# LCD funktionalitet

from machine import Pin, PWM  # Importerer Pin og PWM til hardware-styring
from time import sleep  # Importerer sleep-funktion til pauser
from gpio_lcd import GpioLcd  # Importerer LCD-biblioteket til styring af en LCD-skærm

# Instans af LCD-objekt
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),  # Initialiserer LCD med de nødvendige pins
              d4_pin=Pin(33), d5_pin=Pin(32),      # Datapins
              d6_pin=Pin(21), d7_pin=Pin(22),      # Flere datapins
              num_lines=4, num_columns=20)        # Konfigurerer skærmen til 4 linjer og 20 kolonner

################### CONFIGURATION ###################

# Rotary encoder pins
pin_enc_a = 36  # Pin til rotary encoder A-kanal
pin_enc_b = 39  # Pin til rotary encoder B-kanal

##################### OBJEKTER #####################

# Initialiserer rotary encoder pins som input med pull-up-modstand
rotenc_A = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
rotenc_B = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)

############ VARIABLER OG KONSTANTER ############

# Variabel til at holde styr på encoderens aktuelle tilstand
enc_state = 0
# Variabel til at tælle rotationer (positiv eller negativ)
counter = 0

# Konstant for medurs rotation (clockwise)
CW = 1
# Konstant for modurs rotation (counter-clockwise)
CCW = -1

#################### FUNKTIONER ####################

# Rotary encoder truth table. Bestemmer retning baseret på encoderens tilstand
def re_full_step():
    """
    Tjekker rotary encoderens tilstand og returnerer retningen:
    - CW: Medurs rotation
    - CCW: Modurs rotation
    - 0: Ingen rotation
    """
    global enc_state

    # Truth table til full-step rotary encoders
    encTableFullStep = [
        [0x00, 0x02, 0x04, 0x00],
        [0x03, 0x00, 0x01, 0x10],
        [0x03, 0x02, 0x00, 0x00],
        [0x03, 0x02, 0x01, 0x00],
        [0x06, 0x00, 0x04, 0x00],
        [0x06, 0x05, 0x00, 0x20],
        [0x06, 0x05, 0x04, 0x00]]

    # Opdaterer enc_state baseret på A- og B-kanalens værdier
    enc_state = encTableFullStep[enc_state & 0x0F][(rotenc_B.value() << 1) | rotenc_A.value()]
    
    # Bestemmer rotationsretning
    result = enc_state & 0x30
    if result == 0x10:  # Medurs rotation
        return CW
    elif result == 0x20:  # Modurs rotation
        return CCW
    else:  # Ingen rotation
        return 0

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

# # Ikondata til en pil (kommenteret ud)
# arrow_icon = [0b00000,
#                0b00100,
#                0b01110,
#                0b11111,
#                0b00100,
#                0b00100,
#                0b00100,
#                0b00000]
# # Gemmer pilikonet på plads 1 (kommenteret ud)
# set_icon(lcd, 1, arrow_icon)

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