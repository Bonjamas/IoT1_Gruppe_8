# Copyright 2024 - KEA - ITTEK - IoT - GRUPPE8
# Christoffer Sander Jørgensen
# Mere info www.gruppe8.dk

# LCD funktionalitet

from machine import Pin, PWM
from time import sleep
from machine import Pin
from gpio_lcd import GpioLcd

# Instans af LCD Objekt
lcd = GpioLcd(rs_pin=Pin(27), enable_pin=Pin(25),
              d4_pin=Pin(33), d5_pin=Pin(32),
              d6_pin=Pin(21), d7_pin=Pin(22),
              num_lines=4, num_columns=20)

################### CONFIGURATION ###################

# Rotary encoder pins
pin_enc_a = 36
pin_enc_b = 39

##################### OBJEKTER #####################

# Instatiere objekterne til LCD'en
rotenc_A = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
rotenc_B = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)

############ VARIABLER OG KONSTANTANTER ############

# Encoder state control variabel
enc_state = 0                          
# counter stiger eller falder ved rotation
counter = 0                            

# Konstant clock wise rotation
CW = 1
# Konstant counter clock wise rotation
CCW = -1                              

#################### FUNKTIONER ####################

# Rotary encoder truth table, Hvilken en man skal bruge afhænger af rotary encoder hardware
def re_full_step():
    global enc_state

    encTableFullStep = [
        [0x00, 0x02, 0x04, 0x00],
        [0x03, 0x00, 0x01, 0x10],
        [0x03, 0x02, 0x00, 0x00],
        [0x03, 0x02, 0x01, 0x00],
        [0x06, 0x00, 0x04, 0x00],
        [0x06, 0x05, 0x00, 0x20],
        [0x06, 0x05, 0x04, 0x00]]

    enc_state = encTableFullStep[enc_state & 0x0F][(rotenc_B.value() << 1) | rotenc_A.value()]
 
    # -1: Venstre/CCW, 0: ingen rotation, 1: Højre/CW
    result = enc_state & 0x30
    if (result == 0x10):
        return CW
    elif (result == 0x20):
        return CCW
    else:
        return 0

# Funktion til at lave ikoner og gemme dem
def set_icon(lcd, location, char_map):
    location &= 0x07 									# (0-7) er ledige
    lcd.custom_char(location, bytearray(char_map))
    
# 1. ikon (batteri) 
battery_icon = [0b00000,
                0b01110,
                0b11111,
                0b10001,
                0b10011,
                0b10111,
                0b11111,
                0b11111]

# 1. ikon (batteri) gemt på plads 0
set_icon(lcd, 0, battery_icon) 

# # 2. ikon (pil) 
# arrow_icon = [0b00000,
#               0b00100,
#               0b01110,
#               0b11111,
#               0b00100,
#               0b00100,
#               0b00100,
#               0b00000]
# 
# # 2. ikon (pil) gemt på plads 1
# set_icon(lcd, 1, arrow_icon) 

# Skriver til LCD displayet samt bestemmer hvor den skal starte
def write(linje, kolonne, tekst, ikon = " "):
    lcd.move_to(kolonne, linje) 
    lcd.putstr(str(tekst) + ikon + " ")

# Rydder LCD displayet
def clear():
    lcd.clear()



