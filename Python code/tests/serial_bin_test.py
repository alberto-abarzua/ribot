from sre_constants import IN
import serial
import time
import random
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_control.bins import *
from arm_control.status import *

"""

Tests for the arduino serial comunication.  (not unittesting)


"""


def run(m):
    m = m.encode()
    arduino.write(m)


def my_read(times = -1,show = True):
    while(times < 0 or times >0):
        res = arduino.read(1)
        try:
            res = res.decode()
            assert(res == READY_STATUS)
            if(res == "\r\n<LOOP>;"):
                continue;
            if(show):
                print(res)
        except:
            print("invalid char")
        times -=1

def stress(iters):
    commands = [("m",1)]
    results = np.zeros(iters);
    print("Starting stress test")
    for i in range(iters):
        print(i,"/",iters,end = "\r")
        op,code = random.choice(commands)
        start = time.perf_counter()
        run(Message(op,code,[random.randint(-100,100) for _ in range(6)]))
        my_read(1,show= False)
        end = time.perf_counter()
        results[i] += (end-start)
    return results


if __name__=="__main__":
    #Coms init.
    arduino = serial.Serial(baudrate = 115200,port ="COM6",timeout=5)
    arduino.close()
    arduino.open()

    if (arduino.read(1).decode() == INITIALIZED):
        print("Arduino initilized")



    s_start= time.perf_counter()
    r = stress(9000)
    s_end = time.perf_counter()
    print("Average time between command and response",np.average(r),"lasting overall ",(s_end-s_start),"seconds")