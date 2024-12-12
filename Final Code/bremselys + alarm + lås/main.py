from time import sleep
from uthingsboard.client import TBDeviceMqttClient
import gc
import secrets
from functions import initialize_imu, set_brake_light, check_brake, np_clear, alarm, control_solenoid

# Konfigurationer
SCL_PIN = 18
SDA_PIN = 19

# Global variabler
alarm_enabled = False
solenoid_enabled = False

# Initialisering
imu = initialize_imu()

# ThingsBoard MQTT klient
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)

def handler(req_id, method, params):
    """
    Handler callback til RPC fra ThingsBoard.
    """

    global alarm_enabled, solenoid_enabled
    try:
        if method == "toggle_alarm":
            if params == "1" or params == 1:
                alarm_enabled = True
                print("Alarm aktiveret")
            else:
                alarm_enabled = False
                print("Alarm deaktiveret")
                np_clear()

        if method == "toggle_solenoid":
            if params == "1" or params == 1:
                solenoid_enabled = True
                control_solenoid(True)
                alarm_enabled = True  # Sørg for at alarm aktiveres ved solenoid
                print("Alarm aktiveret via solenoid")
            else:
                solenoid_enabled = False
                control_solenoid(False)
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
        client.check_msg()

        if alarm_enabled or solenoid_enabled:
            imu_data = imu.get_values()
            if imu_data["acceleration x"] < -5000:
                alarm()
            else:
                np_clear()
        else:
            check_brake(imu, alarm_enabled)

        if gc.mem_free() < 2000:
            gc.collect()

        sleep(0.1)

except KeyboardInterrupt:
    print("Afslutter program...")
    client.disconnect()
    np_clear()