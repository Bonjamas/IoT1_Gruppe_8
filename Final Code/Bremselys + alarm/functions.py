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

def setup_imu(scl_pin, sda_pin):
    """Opsætning af I2C-forbindelse til MPU6050."""
    i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))
    return MPU6050(i2c)  # Initialiser MPU6050 med I2C

def setup_neopixels(pin, num_pixels):
    """Opsætning af NeoPixel-ring."""
    return NeoPixel(Pin(pin), num_pixels)

def set_brake_light(neopixels, state):
    """Opdaterer NeoPixel-ringen til bremselys."""
    if state:
        for i in range(len(neopixels)):
            neopixels[i] = (255, 0, 0)  # Rød farve
    else:
        for i in range(len(neopixels)):
            neopixels[i] = (0, 0, 0)  # Sluk
    neopixels.write()

def blink_brake_light(neopixels, blinks, frequency):
    """Blinker bremselyset et bestemt antal gange."""
    for _ in range(blinks):
        set_brake_light(neopixels, True)  # Tænd bremselyset
        sleep(frequency)
        set_brake_light(neopixels, False)  # Sluk bremselyset
        sleep(frequency)

def check_brake(imu, neopixels, alarm_enabled):
    """Kontrollerer bremselyset baseret på accelerationsdata."""
    if not alarm_enabled:  # Kun tænd bremselys, hvis alarm ikke er aktiveret
        try:
            imu_data = imu.get_values()
            ax = imu_data["acceleration y"]

            if ax < -5000.0:  # Justér efter behov
                blink_brake_light(neopixels, 3, 0.2)  # Blink 3 gange
            else:
                set_brake_light(neopixels, True)
        except Exception as e:
            print(f"Fejl ved aflæsning: {e}")
            set_brake_light(neopixels, False)
    else:
        np_clear()

def clear_neopixels(neopixels):
    """Slukker alle NeoPixels."""
    for i in range(len(neopixels)):
        neopixels[i] = (0, 0, 0)
    neopixels.write()