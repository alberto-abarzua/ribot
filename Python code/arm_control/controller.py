import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_control.arduino_dummy import DummyArduino
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

        self.acc = 10000 #Acurray of the angles sent to the arduino.
        self.num_joints = 6
        

    def read(self): 
        """Read a line from the arduino.

        Returns:
            str: decoded line read from the arduino
        """
        return self.arduino.readline().decode()
    
    def move_command(self,angles):
        """Sends a move command to the arduino.

        Args:
            angles (list[Angle]): list of angles the joints should move from their current pos.
        """
        rad_times_acc_angles = [str(int(angle.rad*self.acc)) for angle in angles]
        # Joint 1 has 2 motors
        rad_times_acc_angles.insert(1,rad_times_acc_angles[1])
        command = "m{} ".format(self.num_joints +1)
        command += " ".join(rad_times_acc_angles)
        self.arduino.write(command.encode())

    def wait(self):
        """Runs a sleep timer until the arduino is ready to receive more data.
        """
        while(self.read() != "0\n"):
            time.sleep(0.00001)

    def move_to(self,joints):
        """Empty for now

        Args:
            joints (list[Angle]): list of angles the joints should add to current angles.
        """
        pass

   