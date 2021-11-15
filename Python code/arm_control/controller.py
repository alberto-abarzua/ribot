import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arduino_dummy import DummyArduino
import serial
import time
from arm_utils.armTransforms import Angle
import arm_utils.robotarm as robotarm

__author__ = "Alberto Abarzua"

class Controller():
    """Controller class, has all the controlls of the robot arm.
    """

    def __init__(self,port = None,baudrate = None) -> None:
        """Controller constructor. Creates the serial conection to the arduino. If there isn't a port or
        baudrate, a DummyArduino will be used (For testing)

        Args:
            port (string, optional): COM port of the arduino. Defaults to None.
            baudrate (int, optional): BaudRate of the arduino. Defaults to None.
        """
        # Conection to arduino
        if (port is None or baudrate is None): #Used during testing.
            self.arduino = DummyArduino()
        else:
            self.arduino = serial.Serial(baudrate = baudrate,port = port)
            self.arduino.baudrate = baudrate
            try:
                self.arduino.open()
            except Exception as e:
                print("Error opening serial port: " +str(e) )
        # Robot arm initialization
        
        robot = robotarm.RobotArm()

        #Physical paramters in mm.
        robot.a2x = 0
        robot.a2z = 178
        robot.a3z = 156
        robot.a4x = 54
        robot.a5x = 116
        robot.a6x = 156
        

    def read(self) -> str: 
        """Read a line from the arduino.

        Returns:
            str: decoded line read from the arduino
        """
        return self.arduino.readline().decode()

    def wait(self) -> None:
        """Runs a sleep timer until the arduino is ready to receive more data.
        """
        while(self.read() != "0\n"):
            time.sleep(0.00001)

    def moveTo(self,joints):

   