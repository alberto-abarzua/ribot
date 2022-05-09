import serial
import time
from arm_control.bins import *
import struct

import string
import random



arduino = serial.Serial(baudrate = 9600,port ="COM6")
arduino.close()
arduino.open()

print("c".encode())
time.sleep(1)

val = ""



for _ in range(10):
    args = [random.randint(-21321313,21321313) for i in range(random.randint(0,10))]
    m = Message(random.choice(string.ascii_letters),random.randint(0,10),args)
    m = m.encode()
    arduino.write(m)
    time.sleep(0.001)
    res = arduino.read_until()
    print(res.decode())
