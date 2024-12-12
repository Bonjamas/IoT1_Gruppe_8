from time import sleep
from machine import Pin, PWM, I2C
from neopixel import NeoPixel
from mpu6050 import MPU6050

# BUZZER og NeoPixel-konfiguration
n = 12  # Antal NeoPixels
p = 12  # GPIO-pin til NeoPixel-striben
buzzer = PWM(Pin(26, Pin.OUT), duty=0)
np = NeoPixel(Pin(p, Pin.OUT), n)

def initialize_imu():
    """Initialiserer I2C og MPU6050."""
    i2c = I2C(0)  # Standard GPIO til SDA/SCL
    imu = MPU6050(i2c)
    return imu

def set_color(r, g, b):
    """Sætter alle NeoPixels til en bestemt farve."""
    for i in range(n):
        np[i] = (r, g, b)
    np.write()

def np_clear():
    """Slukker alle NeoPixels."""
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

def alarm():
    """Afspiller en alarm med lys og lyd."""
    for _ in range(5):  # Kør alarmen 5 gange
        set_color(255, 0, 0)  # Tænd rødt lys
        buzzer.duty(512)
        buzzer.freq(440)  # Lav tone
        sleep(0.5)

        np_clear()  # Sluk lyset
        buzzer.duty(512)
        buzzer.freq(1012)  # Høj tone
        sleep(0.5)

    # Sluk alarmen efter gentagelser
    np_clear()
    buzzer.duty(0)
