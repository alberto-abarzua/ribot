from math import e
from pickletools import ArgumentDescriptor
import serial
import sys
import os
from collections import defaultdict
import time

from sklearn.linear_model import ARDRegression
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arm_control.status import *
from arm_control.bins import *
from arm_control.arduino_dummy import DummyArduino
from arm_control.bins import message2command

from serial.serialutil import SerialException

import keyboard


class SerialMonitor:

    def __init__(self,controller= None,port = None,baudrate = None ) -> None:
        self.sta_dict = defaultdict(lambda : UNK)
        self.sta_dict["m"] = READY_STATUS
        self.sta_dict["i"] = PRINTED
        self.controller = controller
        self.lock = None
        if(controller is not None):
            self.lock = controller.coms_lock

        print("Conecting to arduino...")

        if (port is None or baudrate is None):  # Used during testing.
            self.arduino = DummyArduino()
        else:
            self.arduino = serial.Serial(baudrate=baudrate, port=port)
            try:
                self.arduino.close()
                self.arduino.open()
                if (self.arduino.read(1).decode() == INITIALIZED):
                    print("Arduino is initialized!")
            except SerialException as e:
                print("Error opening serial port: " + str(e))

    def write(self,bytes):
        """Writes bytes to the arduino.

        Args:
            bytes (b''): sequence of bytes to be written.
        """
        self.arduino.write(bytes)

    def read(self,nbytes =1):
        """Read a line from the arduino.
         Args:
            nbytes (int): number of bytes that will be read
        Returns:
            str: decoded line read from the arduino
        """
        if (self.arduino.in_waiting >= 1):
            val = self.arduino.read(nbytes)
            try:
                val.decode()
            except Exception as e:
                print(str(e), "value that caused the error: ", val)
                return None
            return val.decode().strip()
        return None

    def upper_read(self,status):
        if (status == PRINTED):
            self.lock.acquire()
            res = self.arduino.read_until(PRINTED.encode())
            self.lock.release()
        else:
            return

        try:
            res = res.decode()
            print(res)
        except:
            print("Value that generated the error {}".format(res))


    def send_command(self,command):
        """Sends a command to the arduino. Sends the command's message to the arduino.

        Args:
            command (Command): Calls the send method on a command, (sends it's message to the arduino)
        """
        if (command.is_correct()):
            self.lock.acquire()
            command.send()
            self.wait()
            self.lock.release()

    def wait(self):
        """Runs a sleep timer until the arduino is ready to receive more data.
        """
        if(self.read() == BUSY ):
            print("Busy...")
            while (self.read() != CONTINUE):
                time.sleep(0.0001)
            print("Continuing")
        self.arduino.flush()

    def run_direct(self,message):
        """Writes the enconded version of a message to the arduino

        Args:
            message (Message): message that will be written.
        """
        command = message2command(message,self.controller)
        if command is None:
            self.lock.acquire()
            self.arduino.write(message.encode())
            self.lock.release()
        else:
            self.send_command(command)


    def interp(self,mes):
        """Interps a string containing a message

        Args:
            mes (str): string that contains a message

        Returns:
            Tuple (Message,str,Bool):  Returns the message, the operation of the message, and a bool if the code should be looped.
        """
        if "txt" in mes: #We want to run a script.
            return "text",mes,False
        loop = False
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
        return m,op,loop

    def run(self):
        """Used to run the a interactive serial monitor through terminal.
        """
        while(True):
            
            mes = input("Please enter Message:")
            
            try:
               m,op,loop = self.interp(mes)    
            except:
                print("Please enter a valid input.")
                continue;
            if m == "text":
                try:
                    with open("arm_control/scripts/"+op) as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            new_mes,op,loop = self.interp(line)  
                            self.run_direct(new_mes)
                            self.upper_read(self.sta_dict[op])

                except Exception as e:
                    print(e)
            elif (loop):
                while(True):
                    if keyboard.is_pressed("esc"):
                        break
                    time.sleep(0.1)
                    self.run_direct(m)
                    self.upper_read(self.sta_dict[op])
            else:   
                self.run_direct(m)
                self.upper_read(self.sta_dict[op])

if __name__ == "__main__":
   
    if (len(sys.argv)== 2):
        PORT = sys.argv[1]
        print("Starting on port {}".format(PORT))
        m = SerialMonitor(None,PORT,115200)
        m.run()
    
    # m1 0 0 0 0 15707 0 