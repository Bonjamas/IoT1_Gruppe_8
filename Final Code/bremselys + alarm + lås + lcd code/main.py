from machine import reset, Pin
from time import sleep
from uthingsboard.client import TBDeviceMqttClient
import gc
import secrets
from functions import initialize_imu, set_brake_light, check_brake, np_clear, alarm, control_solenoid
from gps import gps, get_lat_lon
from lcd_funk import lcd, set_icon, write, clear
from dht11 import dht11, get_temperature

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

        lat_lon = get_lat_lon()         								# retunere lat/lon i tuple format

        lcd.move_to(0,0)		
        lcd.putstr("\x00")
#         lcd_funk.lcd.move_to(0,8)
#         lcd_funk.lcd.putstr("\x01")
#         lcd_funk.write(0,9, float(gps.gps_dtc()), "")						# Viser retning (Nord, Syd, Øst, Vest) på LCD
        write(0,8, float(gps.get_course()), " C")    
        write(1,0, float(round(gps.get_speed(), 2)), " Km/t")	# Viser fart (Km/t) på LCD
        write(1,10, int(get_temperature()), "temp")
        write(2,0, (lat_lon[0]), " lat")
        write(3,0, (lat_lon[1]), " lon")
#        print(f"GPS-vinkel: {gps_course}° -> Retning: {retning}")
         
        if lat_lon:
                                                                              # Gemmer telemetry i dictionary      
            telemetry = {'latitude': lat_lon[0],
                          'longitude': lat_lon[1],
                          'speed':gps.get_speed(),
                          'course':gps.get_course(),
                          'temperature':get_temperature()}
            client.send_telemetry(telemetry) 						# Sender telemetry

        if gc.mem_free() < 2000:
            gc.collect()

        sleep(0.1)

except KeyboardInterrupt:
    print("Afslutter program...")
    client.disconnect()
    np_clear()