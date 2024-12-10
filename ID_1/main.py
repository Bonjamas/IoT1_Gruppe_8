from time import sleep
from batteri import initialize_potmeter, calculate_voltage, calculate_battery_voltage, calculate_battery_percentage

#####
# CONFIGURATION
PIN_POTMETER = 34  # GPIO-pin for potmeteret

# Kalibreringskonstanter for batterispænding
VOLTAGE_LOW = 1070
VOLTAGE_HIGH = 2430
a = (4.2 - 3.0) / (VOLTAGE_HIGH - VOLTAGE_LOW)
b = 3.0 - a * VOLTAGE_LOW

#####
# INITIALISATION
potmeter_adc = initialize_potmeter(PIN_POTMETER)
print("ADC and potmeter test\n")

#####
# PROGRAM
try:
    while True:
        adc_val = potmeter_adc.read()
        uadc = calculate_voltage(adc_val)
        battery_voltage = calculate_battery_voltage(adc_val, a, b)
        battery_percentage = calculate_battery_percentage(battery_voltage)

        print(f"ADC Value: {adc_val}")
        print(f"Measured Voltage: {uadc:.2f} V")
        print(f"Battery Voltage: {battery_voltage:.2f} V")
        print(f"Battery Percentage: {battery_percentage:.2f}%\n")

        sleep(0.2)

except KeyboardInterrupt:
    print("Program stopped by user.")
