from sre_constants import IN
from unittest.mock import DEFAULT
import serial
import time
import random
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_control.bins import *
from arm_control.status import *

import unittest


"""

Tests for the arduino serial comunication.  Must be connected to real arduino with firmware.


Port to be used should be defined here:

"""
DEFAULT_PORT  = "COM8"


class serial_bin_test(unittest.TestCase):

    def my_run(self,m):
        m = m.encode()
        self.arduino.write(m)


    def my_read(self,times = -1,show = True):
        while(times < 0 or times >0):
            res = self.arduino.read(1)
            try:
                res = res.decode()
                assert(res == READY_STATUS)
                
            except:
                print("invalid char {}".format(res))
            times -=1

    def stress(self,iters):
        commands = [("m",1)]
        results = np.zeros(iters);
        print("Starting stress test")
        for i in range(iters):
            print(i,"/",iters,end = "\r")
            op,code = random.choice(commands)
            start = time.perf_counter()
            self.my_run(Message(op,code,[random.randint(-6000,6000) for _ in range(6)]))
            self.my_read(1,show= False)
            end = time.perf_counter()
            results[i] += (end-start)
        return results



    def setUp(self):
        port = DEFAULT_PORT
        arduino = serial.Serial(baudrate = 115200,port =port,timeout=5)
        arduino.close()
        arduino.open()
        self.arduino = arduino
        if (self.arduino.read(1).decode() == INITIALIZED):
            self.ini = True

    def step0(self):
        self.assertTrue(self.ini)
    def step1(self):
        self.my_run(Message("m",1,[900,900,900,900,900,900]))
        self.my_run(Message("i",1,[]))
        res = self.arduino.read_until(PRINTED.encode()).decode()
        self.assertTrue("angles:  900 900 900 900 900 900" in res)





    def step2(self):
        self.my_run(Message("m",1,[900,900,900,900,900,900]))
        
        self.my_run(Message("t",1,[900,12,24,34,53,35]))

        res = self.arduino.read_until(PRINTED.encode()).decode()
        self.assertEqual(res,"1Message: Op: t1 args (  <=> 900 <=> 12 <=> 24 <=> 34 <=> 53 <=> 35 );")

    def step3(self):
        self.my_run(Message("i",2,[]))
        res = self.arduino.read_until(PRINTED.encode()).decode()
        self.assertEqual(res,"Num motors 7  -  \r\nJoint 0  nmotors: 1\r\nJoint 1  nmotors: 2\r\nJoint 2  nmotors: 1\r\nJoint 3  nmotors: 1\r\nJoint 4  nmotors: 1\r\nJoint 5  nmotors: 1\r\n\r\n;")

    def step4(self):
        self.my_run(Message("i",1,[]))
        res = self.arduino.read_until(PRINTED.encode()).decode()
        self.assertTrue("angles:  1800 1800 1800 1800 1800 1800" in res)

    def step5(self):
        "Stress test"
        s_start= time.perf_counter()
        r = self.stress(500)
        s_end = time.perf_counter()
        print("Average time between command and response",np.average(r),"lasting overall ",(s_end-s_start),"seconds")

    def step6(self):
        self.my_run(Message("i",3,[]))
        res = self.arduino.read_until(PRINTED.encode()).decode()
        self.assertEqual(res,"Sensors:  S1 OFF S2 OFF S3 OFF S4 OFF S5 OFF S6 OFF;")



    def steps(self):
        for name in sorted(dir(self)):
            if name.startswith("step"):
                yield name, getattr(self, name) 

    def test_steps(self):
        for name, step in self.steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))

if __name__=="__main__":
    """Must be ran with the port as argument. 
    
    
    "python serial_bin_test.py <PORT>"

    """


    if (len(sys.argv) ==1):
        port = DEFAULT_PORT
    else:
        port = sys.argv[1]
    
    unittest.main()
    

