from math import e
from pickletools import ArgumentDescriptor
import serial
import sys
import os
from collections import defaultdict
import time

from sklearn.linear_model import ARDRegression
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arm_utils.status import *
from arm_utils.bins import *
from arm_utils.arduino_dummy import DummyArduino
from arm_utils.bins import message2command

from serial.serialutil import SerialException

import keyboard


class SerialMonitor:
    """Serial monitor class, used to manage the serial comunications to the arduino for the controller. Also an interactive console
    program can be ran to send commands directly to the arduino.
    """
    def __init__(self,controller= None,port = None,baudrate = None ) -> None:
        """Serial monitor constructor starts the comunications with the arduino (opens serial port.)
        If port and buadrate are none, the serial monitor will run with an arduino dummy (arm_utils/arduino_dummy)

        Args:
            controller (Controller, optional): Controller that will use the serial monitor. Defaults to None.
            port (str, optional): Port to use in serial connection. Defaults to None.
            baudrate (int, optional): baudrate to use in serial connection. Defaults to None.
        """
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

    def monitor_read(self,status):
        """Used to read (receive responses) from the arduino when running the interactive console version of the serial monitor.    

        Args:
            status (int): Status that should be expected whehn reading.
        """
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
            with self.lock:
                command.send()
                self.wait()

    def wait(self):
        """Runs a sleep timer until the arduino is ready to receive more data.
        """

        if(self.read() == BUSY ):
            print("\nBusy...\n")
            while (self.read() != CONTINUE):
                pass
            print("\nContinuing\n")
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
                            self.monitor_read(self.sta_dict[op])

                except Exception as e:
                    print(e)
            elif (loop):
                while(True):
                    if keyboard.is_pressed("esc"):
                        break
                    time.sleep(0.1)
                    self.run_direct(m)
                    self.monitor_read(self.sta_dict[op])
            else:
                self.run_direct(m)

                self.monitor_read(self.sta_dict[op])


if __name__ == "__main__":
   
    if (len(sys.argv)== 2):
        PORT = sys.argv[1]
        print("Starting on port {}".format(PORT))
        m = SerialMonitor(None,PORT,115200)
        m.run()
    