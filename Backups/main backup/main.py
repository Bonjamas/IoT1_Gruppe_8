from machine import Pin, I2C
from time import sleep, ticks_ms
from uthingsboard.client import TBDeviceMqttClient
import gc
import secrets
from alarm_laas_lys import set_brake_light, check_brake, np_clear, alarm, control_solenoid
from gps import gps, get_lat_lon
from lcd import lcd, set_icon, write, clear
from dht11 import get_temperature
from ina219_lib import INA219
from mpu6050 import MPU6050
import sys

# Global variables
alarm_enabled = False
solenoid_enabled = False

# Initialization
i2c = I2C(0)  # Standard GPIO til SDA/SCL
imu = MPU6050(i2c)
ina = INA219(i2c)

# ThingsBoard MQTT client
client = TBDeviceMqttClient(secrets.SERVER_IP_ADDRESS, access_token=secrets.ACCESS_TOKEN)

# RPC Handler
def handler(req_id, method, params):
    """
    Handles RPC requests from ThingsBoard.
    """
    global alarm_enabled, solenoid_enabled
    try:
        if method == "toggle_alarm":
            alarm_enabled = bool(int(params))
            if alarm_enabled:
                print("Alarm activated")
                lcd.clear()  # Clear LCD when alarm is activated
            else:
                print("Alarm deactivated")
                np_clear()

        elif method == "toggle_solenoid":
            solenoid_enabled = bool(int(params))
            control_solenoid(solenoid_enabled)
            alarm_enabled = solenoid_enabled  # Synchronize alarm with solenoid state
            lcd.clear()
            print(f"Solenoid {'activated' if solenoid_enabled else 'deactivated'}")
            if not solenoid_enabled:
                np_clear()

    except Exception as e:
        print(f"Error in RPC handler: {e}")

# Connect to ThingsBoard
client.connect()
client.set_server_side_rpc_request_handler(handler)
print("Connected to ThingsBoard")

# Sensor monitoring and telemetry loop
start = ticks_ms()
while True:
    try:
        client.check_msg()

        if alarm_enabled or solenoid_enabled:
            imu_data = imu.get_values()
            if imu_data.get("acceleration x") < -5000:  # Handle missing data safely
                alarm()
            else:
                np_clear()
        else:
            check_brake(imu, alarm_enabled)
#             print(imu.get_values()) # Bruges til at se retning ift bremselys

        if ticks_ms() - start > 5000:
            if not alarm_enabled:  # Only update LCD if alarm is off
                # Retrieve INA219 data with error handling
                current = ina.get_current()
                voltage = ina.get_bus_voltage()
                battery_percent = max(0, min(100, ((voltage - 6) / (8.4 - 6)) * 100))
                remaining_time = (((battery_percent / 100) * 1800) / current)

                # Get GPS data
                lat_lon = get_lat_lon() or (0, 0)

                # Display data on LCD
                lcd.move_to(0, 0)
                lcd.putstr("\x00")
                write(0, 1, int(battery_percent), "%")
                write(0, 5, int(remaining_time), "h")
                write(0, 10, gps.get_course(), "C")
                write(1, 0, round(gps.get_speed(), 2), " Km/t")
                write(1, 10, int(get_temperature()), " temp")
                write(2, 0, lat_lon[0], " lat")
                write(3, 0, lat_lon[1], " lon")

                # Send telemetry
                telemetry = {
                    'latitude': lat_lon[0],
                    'longitude': lat_lon[1],
                    'speed': gps.get_speed(),
                    'course': gps.get_course(),
                    'temperature': get_temperature(),
                    'batteryLevel': battery_percent,
                    'capacity': remaining_time,
                }
                client.send_telemetry(telemetry)
            start = ticks_ms()
            
        # Free memory if necessary
        if ticks_ms() - start > 10000:
            if gc.mem_free() < 2000:
                gc.collect()

    except Exception as e:
        print(e)

    except KeyboardInterrupt:
        print("Exiting program...")
        client.disconnect()
        np_clear()
        lcd.clear()
        sys.exit()