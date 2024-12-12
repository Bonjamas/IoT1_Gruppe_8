from functions import setup_imu, setup_neopixels, check_brake, clear_neopixels, set_brake_light
from time import sleep

# Konfigurationer
SCL_PIN = 18
SDA_PIN = 19
NEOPIXEL_PIN = 12
NUM_PIXELS = 12

# Initialisering
i2c_device = setup_imu(SCL_PIN, SDA_PIN)
neopixels = setup_neopixels(NEOPIXEL_PIN, NUM_PIXELS)

# Loop der konstant overvåger acceleration
try:
    while True:
        check_brake(i2c_device, neopixels)
        sleep(0.1)
except KeyboardInterrupt:
    set_brake_light(neopixels, False)  # Sluk NeoPixel-ring ved afslutning
    clear_neopixels(neopixels)
    print("Afsluttet.")