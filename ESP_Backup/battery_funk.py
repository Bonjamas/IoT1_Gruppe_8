from machine import ADC, Pin



def initialize_potmeter(pin_potmeter):
    """
    Initialiser potmeteret på den angivne GPIO-pin.
    """
    potmeter_adc = ADC(Pin(pin_potmeter))
    potmeter_adc.atten(ADC.ATTN_11DB)  # Fuldt spændingsområde (op til 3.3V)
    return potmeter_adc

def calculate_voltage(adc_value):
    """
    Beregner spændingen fra en ADC-værdi.
    """
    max_adc_value = 4095  # 12-bit opløsning
    max_voltage = 3.3  # Maksimal spænding
    return (adc_value / max_adc_value) * max_voltage

def calculate_battery_voltage(adc_value, a, b):
    """
    Beregner batterispænding baseret på ADC-værdi og kalibreringskonstanter.
    """
    return (a * adc_value) + b

def calculate_battery_percentage(battery_voltage):
    """
    Beregner batteriets procentdel baseret på spænding.
    """
    min_voltage = 3.0  # Minimal batterispænding
    max_voltage = 4.2  # Maksimal batterispænding
    return ((battery_voltage - min_voltage) / (max_voltage - min_voltage)) * 100

