from pickletools import ArgumentDescriptor
import serial
import sys
import os
from collections import defaultdict
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arm_control.status import *
from arm_control.bins import *

PORT = "COM8"

class Monitor():

    def __init__(self) -> None:
        port = PORT
        self.sta_dict = defaultdict(lambda : UNK)
        self.sta_dict["m"] = READY_STATUS
        self.sta_dict["i"] = PRINTED


        arduino = serial.Serial(baudrate = 115200,port =port,timeout=5)
        arduino.close()
        arduino.open()
        self.arduino = arduino
        if (self.arduino.read(1).decode() == INITIALIZED):
            self.ini = True
            print("Arduino is initialized!")

    def my_run(self,m):
        m = m.encode()
        self.arduino.write(m)

    def read(self,status):
        if (status == PRINTED):
            res = self.arduino.read_until(PRINTED.encode())
        else:
            return
        try:
            res = res.decode()
            print(res)
        except:
            print("Value that generated the error {}".format(res))

    def interp(self,mes):
        mes = mes.split(" ")
        op = mes[0][0]
        if(op == ":"):
            op = mes[0][1]
            mes[0] = mes[0][1:]
            loop = True
        code = int(mes[0][1:])
        args = mes[1:]
        args = [int(x) for x in args]
        m = Message(op,code,args)
        return m,op

    def run(self):
        while(True):
            
            mes = input("Please enter Message:")
            loop = False
            
            try:
               m,op = self.interp(mes)
            except:
                print("Please enter a valid input.")
                continue;
            if (loop):
                while(True):
                    self.my_run(m)
                    self.read(self.sta_dict[op])
            else:
                self.my_run(m)
                self.read(self.sta_dict[op])


if __name__ == "__main__":
   
    if (len(sys.argv)== 2):
        PORT = sys.argv[1]
        print("Starting on port {}".format(PORT))
        m = Monitor()
        m.run()
    elif (len(sys.argv) >=3):
        PORT = sys.argv[1]
        file = sys.argv[2]
        m = Monitor()
        times = 1
        if (len(sys.argv) == 4):
            times = int(sys.argv[3])
        with open(file="scripts/" + file) as f:
            lines =  f.readlines()
            for _ in range(times):
                n=0
                for line in lines:
                    mes,op = m.interp(line)
                    m.my_run(mes)
                    if m.arduino.in_waiting >=1:
                        res =m.arduino.read(1).decode()
                        if (int(res) == 2):
                            print("Ran {} commands before receiving BUSY".format(n))
                            m.my_run(Message("i",4))

                            break
                    n+=1
            time.sleep(4)
            m.my_run(Message("i",4))
            s = m.arduino.read_all()
            print(s.decode())
    
    

"""_summary_

m1 7853 0 0 0 0 0
i1
m1 -7853 0 0 -0 -0 -0
:i1


"""