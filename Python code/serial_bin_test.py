from socket import timeout
import serial
import time
from arm_control.bins import *
import struct

import string
import random



arduino = serial.Serial(baudrate = 9600,port ="COM6",timeout=5)
arduino.close()
arduino.open()

time.sleep(1)

val = ""

def run(m):
    m = m.encode()
    arduino.write(m)
    time.sleep(0.2)
    res = arduino.read_until(";".encode(),)
    print(res.decode())



run(Message("d",1,[]))
run(Message("k",1,[]))

run(Message("d",1,[]))
# run(Message("k",1,[900,200,900,900,900,3]))

# time.sleep(0.2)

# run(Message("k",1,[]))
