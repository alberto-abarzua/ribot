import os.path
import sys

from serial.serialutil import SerialException
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
            if not self.arduino.isOpen():
                try:
                    self.arduino.open()
                except SerialException as e:
                    print("Error opening serial port: " +str(e) )
        # Robot arm initialization
        
        self.robot = robotarm.RobotArm()

        #Physical paramters in mm.
        self.robot.a2x = 0
        self.robot.a2z = 178
        self.robot.a3z = 156
        self.robot.a4x = 54
        self.robot.a5x = 116
        self.robot.a6x = 156

        self.acc = 10000 #Acurray of the angles sent to the arduino.
        self.num_joints = 6
        self.angles = [Angle(0,"rad") for _ in range(self.num_joints)]
        self.arduino_angles = [0 for _ in range(self.num_joints)]

        

    def read(self): 
        """Read a line from the arduino.

        Returns:
            str: decoded line read from the arduino
        """
        return self.arduino.readline().decode()

    def update_arduino_angles(self,angles):
        """Updates the angles that represnt the current angles array in the arduino. 

        Args:
            angles (list[Angle]): list of angles that will be added to arduino_angles
        """
        for i in range(len(angles)):
            self.arduino_angles[i] += angles[i]
        self.robot.angles = self.get_arduino_angles()
        
    def get_arduino_angles(self):
        """Gets the current arduino angles in Angle format.

        Returns:
            list[Angles]: current angles tracked.
        """
        return [Angle(x/self.acc,"rad") for x in self.arduino_angles]

    def move_command(self,angles):
        """Sends a move command to the arduino.

        Args:
            angles (list[Angle]): list of angles the joints should move from their current pos.
        """
        rad_times_acc_angles = [str(round(angle.rad*self.acc)) for angle in angles]

        self.update_arduino_angles([int(x) for x in rad_times_acc_angles ])#Keep track of the angles sent.
        
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

    def move_to_angle_config(self,angles):
        """Makes the robot go to a certain angle configuration (this is absolute positioning).

        Args:
            angles (list[Angles]): Angles to go to.
        """
        cur_angles = self.get_arduino_angles()
        dif = [Angle(fin.rad-ini.rad,"rad")for  ini,fin in zip(cur_angles,angles)]
        self.move_command(dif)

    def move_to_point(self,cords,angles):
        """Makes the tcp move to cords and certain euler angles. This is a point to point movement.

        Args:
            cords (list[int]): list x,y,z coords of the tcp to reach
            angles (list[Angle]): euler angles the tcp should have.
        """
        next_angles = self.robot.inverse_kinematics((cords,angles))
        if (next_angles is None):
            return "Angles out of reach"
        self.move_to_angle_config(next_angles)
        
        
        

   