from time import sleep
from machine import Pin, PWM, I2C
from neopixel import NeoPixel
from mpu6050 import MPU6050
from gps_simple import GPS_SIMPLE

# Konstanter
NUM_PIXELS = 12
NEOPIXEL_PIN = 12
BUZZER_PIN = 26
SOLENOID_PIN = 14
GPS_UART = 1  # Change if necessary for your setup

# Initialisering
buzzer = PWM(Pin(BUZZER_PIN, Pin.OUT), duty=0)
np = NeoPixel(Pin(NEOPIXEL_PIN, Pin.OUT), NUM_PIXELS)
solenoid = Pin(SOLENOID_PIN, Pin.OUT)

gps = GPS_SIMPLE(GPS_UART)

def initialize_imu():
    """Initialiserer I2C, MPU6050 (IMU) og INA219 (strømsensor)."""
    i2c = I2C(0)  # Standard GPIO til SDA/SCL
    imu = MPU6050(i2c)
    return imu

def set_color(r, g, b):
    """Sætter alle NeoPixels til en bestemt farve."""
    for i in range(NUM_PIXELS):
        np[i] = (r, g, b)
    np.write()

def np_clear():
    """Slukker alle NeoPixels."""
    for i in range(NUM_PIXELS):
        np[i] = (0, 0, 0)
    np.write()

def alarm():
    """Afspiller en alarm med lys og lyd."""
    for _ in range(5):
        set_color(255, 0, 0)  # Tænd rødt lys
        buzzer.duty(512)
        buzzer.freq(440)  # Lav tone
        sleep(0.5)

        np_clear()  # Sluk lyset
        buzzer.duty(512)
        buzzer.freq(1012)  # Høj tone
        sleep(0.5)

    # Sluk alarmen
    np_clear()
    buzzer.duty(0)

def set_brake_light(state):
    """Opdaterer NeoPixel-ringen til bremselys."""
    color = (255, 0, 0) if state else (0, 0, 0)
    set_color(*color)

def blink_brake_light(blinks, frequency):
    """Blinker bremselyset et bestemt antal gange."""
    for _ in range(blinks):
        set_brake_light(True)
        sleep(frequency)
        set_brake_light(False)
        sleep(frequency)

def check_brake(imu, alarm_enabled):
    """Kontrollerer bremselyset baseret på accelerationsdata."""
    if not alarm_enabled:  # Kun tænd bremselys, hvis alarm ikke er aktiveret
        try:
            imu_data = imu.get_values()
            ax = imu_data["acceleration y"]

            if ax < -5000.0:
                blink_brake_light(3, 0.2)
            else:
                set_brake_light(True)
        except Exception as e:
            print(f"Fejl ved aflæsning: {e}")
            set_brake_light(False)
    else:
        np_clear()

def control_solenoid(state):
    """Styrer solenoid actuator."""
    solenoid.value(state)
    if state:
        print("Solenoid aktiveret")
        sleep(3)  # Hold solenoiden tændt i 3 sekunder
        solenoid.value(0)  # Sluk solenoiden efter 3 sekunder
        print("Solenoid deaktiveret automatisk efter 3 sekunder")
    else:
        print("Solenoid deaktiveret")

def get_gps_location():
    """Henter GPS data og returnerer det som (latitude, longitude)."""
    gps.receive_nmea_data()
    latitude = gps.get_latitude()
    longitude = gps.get_longitude()
    return latitude, longitude
