from machine import Pin, I2C
from time import sleep
import neopixel
from mpu6050 import MPU6050

# Indstil værdi for negativ acceleration
BRAKE_THRESHOLD = -5000.0  # Justér efter behov
BLINK_FREQUENCY = 0.2  # Blinkfrekvens (sekunder)
NUM_BLINKS = 3  # Antal blink ved negativ acceleration

# Opsætning af I2C-forbindelse til MPU6050
i2c = I2C(0, scl=Pin(18), sda=Pin(19))  # Justér pins til din opsætning
imu = MPU6050(i2c)  # Initialiser MPU6050 med I2C

# Opsætning af NeoPixel-ring
NEOPIXEL_PIN = 12  # GPIO-pinnen hvor NeoPixel-ringen er forbundet
NUM_PIXELS = 12  # Antal LEDs på ringen
neopixels = neopixel.NeoPixel(Pin(NEOPIXEL_PIN), NUM_PIXELS)

# Funktion til at opdatere NeoPixel-ringen
def set_brake_light(state):
    if state:
        # Tænd alle pixels med rød farve
        for i in range(NUM_PIXELS):
            neopixels[i] = (255, 0, 0)  # Rød farve
    else:
        # Sluk alle pixels
        for i in range(NUM_PIXELS):
            neopixels[i] = (0, 0, 0)  # Sluk
    neopixels.write()

def np_clear():
    """Slukker alle NeoPixels."""
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

# Funktion til at blinke bremselyset et bestemt antal gange
def blink_brake_light(blinks):
    for _ in range(blinks):
        set_brake_light(True)  # Tænd bremselyset
        sleep(BLINK_FREQUENCY)
        set_brake_light(False)  # Sluk bremselyset
        sleep(BLINK_FREQUENCY)

# Funktion til at kontrollere bremselyset
def check_brake():
    try:
        # Læs accelerationen fra MPU6050 ved hjælp af get_values()
        imu_data = imu.get_values()
        ax = imu_data["acceleration y"]  # Acceleration i x-aksen (m/s^2)

        # Hvis negativ acceleration, blink 3 gange
        if ax < BRAKE_THRESHOLD:
            blink_brake_light(NUM_BLINKS)  # Blink 3 gange
        else:
            set_brake_light(True)  # Tænd bremselyset uden at blinke
    except Exception as e:
        print(f"Fejl ved aflæsning: {e}")
        set_brake_light(False)

# Loop der konstant overvåger acceleration
try:
    while True:
        check_brake()
        sleep(0.1)  # Vent lidt mellem aflæsninger
except KeyboardInterrupt:
    set_brake_light(False)  # Sluk NeoPixel-ring ved afslutning
    np_clear()
    print("Afsluttet.")