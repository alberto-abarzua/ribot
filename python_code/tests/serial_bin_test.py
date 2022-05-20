from sre_constants import IN
from unittest.mock import DEFAULT
import serial
import time
import random
import numpy as np
import os
import sys
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arm_utils.bins as bins
import arm_utils.status as status

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
                assert(res == status.READY_STATUS)
                
            except:
                print("invalid char {}".format(res))
            times -=1
    def readBussy(self):
        if self.arduino.in_waiting>=1:
            res= self.arduino.read(1).decode()
            if(res == status.BUSY ):
                while True:
                    if self.arduino.in_waiting>=1:
                        res= self.arduino.read(1).decode()
                        if (res == status.CONTINUE):
                            break;
        self.arduino.flush()

    def stress(self,iters):
        commands = [("m",1)]
        results = np.zeros(iters);
        print("Starting stress test")
        for i in range(iters):
            print(i,"/",iters,end = "\r")
            op,code = random.choice(commands)
            start = time.perf_counter()
            self.my_run(bins.Message(op,code,[random.randint(-200,200) for _ in range(6)]))
            self.readBussy()
            end = time.perf_counter()
            results[i] += (end-start)
        return results



    def setUp(self):
        port = DEFAULT_PORT
        arduino = serial.Serial(baudrate = 115200,port =port,timeout=5)
        arduino.close()
        arduino.open()
        self.arduino = arduino
        time.sleep(0.5)
        if (self.arduino.read(1).decode() == status.INITIALIZED):
            self.ini = True
            print("Arduino initialized!")

    def step1(self):
        self.my_run(bins.Message("m",1,[100,100,100,100,100,100]))
        time.sleep(0.2)
        self.my_run(bins.Message("i",1,[]))

        res = self.arduino.read_until(status.PRINTED.encode()).decode()
        self.assertTrue("angles:  100 100 100 100 100 100" in res)





    def step2(self):
        self.my_run(bins.Message("m",1,[100,100,100,100,100,100]))

   
    def step4(self):
        self.my_run(bins.Message("i",1,[]))
        res = self.arduino.read_until(status.PRINTED.encode()).decode()
        print(repr(str(res)))
        self.assertTrue("angles:  200 200 200 200 200 200" in res)

    def step5(self):
        "Stress test"
        s_start= time.perf_counter()
        r = self.stress(500)
        s_end = time.perf_counter()
        print("Average time between command and response",np.average(r),"lasting overall ",(s_end-s_start),"seconds")

    def step6(self):
        time.sleep(1)
        self.readBussy()

        self.my_run(bins.Message("i",3,[]))
        res = self.arduino.read_until(status.PRINTED.encode()).decode()
        self.assertEqual(res,"Sensors:  S1 OFF S2 OFF S3 OFF S4 OFF S5 OFF S6 OFF;")
    def step7(self):
        """make sure that all the messages in queues add up to MESSAGE_BUFFER_SIZE *2 -1
        """
        self.readBussy()
        time.sleep(1)
        self.my_run(bins.Message("i",4))
        res = self.arduino.read_until(status.PRINTED.encode()).decode()
        print(res)
        res  = res.split(" ")
        n = 0
        for elem in res:
            if (elem.isdigit()):
                n += int(elem)
        self.assertEqual(n,99)


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
    

