from machine import Pin, I2C
from time import sleep
import neopixel
from mpu6050 import MPU6050

# Indstil værdier
BRAKE_THRESHOLD = -5000.0  # Justér efter behov
BLINK_FREQUENCY = 0.2  # Blinkfrekvens (sekunder)
NUM_BLINKS = 3  # Antal blink ved negativ acceleration

# Opsætning af I2C-forbindelse til MPU6050
def setup_imu(scl_pin, sda_pin):
    i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
    return MPU6050(i2c)  # Initialiser MPU6050 med I2C

# Opsætning af NeoPixel-ring
def setup_neopixels(pin, num_pixels):
    return neopixel.NeoPixel(Pin(pin), num_pixels)

# Funktion til at opdatere NeoPixel-ringen
def set_brake_light(neopixels, state):
    if state:
        for i in range(len(neopixels)):
            neopixels[i] = (255, 0, 0)  # Rød farve
    else:
        for i in range(len(neopixels)):
            neopixels[i] = (0, 0, 0)  # Sluk
    neopixels.write()

def blink_brake_light(neopixels, blinks, frequency):
    for _ in range(blinks):
        set_brake_light(neopixels, True)  # Tænd bremselyset
        sleep(frequency)
        set_brake_light(neopixels, False)  # Sluk bremselyset
        sleep(frequency)

def check_brake(imu, neopixels):
    try:
        imu_data = imu.get_values()
        ax = imu_data["acceleration y"]

        if ax < BRAKE_THRESHOLD:
            blink_brake_light(neopixels, NUM_BLINKS, BLINK_FREQUENCY)
        else:
            set_brake_light(neopixels, True)
    except Exception as e:
        print(f"Fejl ved aflæsning: {e}")
        set_brake_light(neopixels, False)

def clear_neopixels(neopixels):
    for i in range(len(neopixels)):
        neopixels[i] = (0, 0, 0)
    neopixels.write()