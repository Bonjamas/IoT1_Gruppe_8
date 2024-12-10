from machine import Pin
from time import sleep

lock = Pin(14, Pin.OUT)

while True:
    lock.value(0)
    print("deactivated")
    sleep(4)
    lock.value(1)
    print("activated")
    sleep(4)