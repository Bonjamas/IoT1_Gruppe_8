from time import sleep
from uthingsboard.client import TBDeviceMqttClient
import gc
import secrets
from functions import initialize_imu, setup_neopixels, check_brake, clear_neopixels, alarm

# Konfigurationer
SCL_PIN = 18
SDA_PIN = 19
NEOPIXEL_PIN = 12
NUM_PIXELS = 12

# Global variabel til at styre alarmstatus
alarm_enabled = False

# Initialisering
imu = initialize_imu()
neopixels = setup_neopixels(NEOPIXEL_PIN, NUM_PIXELS)

# ThingsBoard MQTT klient
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)

def handler(req_id, method, params):
    """
    Handler callback til RPC fra ThingsBoard.
    """
    global alarm_enabled
    print(f"RPC modtaget: {method}, params: {params}")
    try:
        if method == "toggle_alarm":  # Aktiver/deaktiver alarm
            if params:
                print("Alarm aktiveret")
                alarm_enabled = True
            else:
                print("Alarm deaktiveret")
                alarm_enabled = False
                clear_neopixels(neopixels)

    except Exception as e:
        print(f"Fejl i RPC-handler: {e}")

# Forbind til ThingsBoard
client.connect()
client.set_server_side_rpc_request_handler(handler)
print("Forbundet til ThingsBoard")

# Overvåg sensordata og alarmstatus
try:
    while True:
        # Tjek for nye RPC-kommandoer
        client.check_msg()

        if alarm_enabled:  # Kun hvis alarmen er aktiveret
            values = imu.get_values()
            if values["acceleration z"] < -15000:  # Detekter bevægelse
                alarm()  # Kald alarmfunktionen
            else:
                clear_neopixels(neopixels)

            print(f"Acceleration Z: {values['acceleration z']}")
        else:
            check_brake(imu, neopixels, alarm_enabled)

        # Frigør hukommelse
        if gc.mem_free() < 2000:
            gc.collect()

        sleep(0.1)

except KeyboardInterrupt:
    print("Afslutter...")
    client.disconnect()
    clear_neopixels(neopixels)