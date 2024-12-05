from time import sleep
from uthingsboard.client import TBDeviceMqttClient
import gc
import secrets
from functions import initialize_imu, set_color, np_clear, alarm  # Import funktioner

# Initialiser IMU
imu = initialize_imu()

# Global variabel til at styre alarmstatus
alarm_enabled = False

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
                np_clear()

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
                np_clear()

            print(f"Acceleration Z: {values['acceleration z']}")
        else:
            np_clear()

        # Frigør hukommelse
        if gc.mem_free() < 2000:
            gc.collect()

        sleep(0.1)

except KeyboardInterrupt:
    print("Afslutter...")
    client.disconnect()
    np_clear()
    buzzer.duty(0)
