import os.path
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_control.serial_monitor import SerialMonitor
import numpy as np
import arm_control.commands as com
import arm_utils.robotarm as robotarm
from arm_utils.armTransforms import Angle
from arm_utils.armTransforms import Config
import time
import serial
from arm_control.arduino_dummy import DummyArduino
from arm_control.filemanager import CordAngleInstruction, FileManager, ToolAngleInstruction 

from arm_control.status import *

import threading
__author__ = "Alberto Abarzua"


class Controller():
    """Controller class, has all the controlls of the robot arm.
    """

    def __init__(self, port=None, baudrate=None) -> None:
        """Controller constructor. Creates the serial conection to the arduino. If there isn't a port or
        baudrate, a DummyArduino will be used (For testing)

        Args:
            port (string, optional): COM port of the arduino. Defaults to None.
            baudrate (int, optional): BaudRate of the arduino. Defaults to None.
        """
        # Conection to arduino
       

        self.robot = robotarm.RobotArm()

        # Physical paramters in mm.
        self.robot.a2x = 0
        self.robot.a2z = 172.48
        self.robot.a3z = 173.5
        self.robot.a4z = 0

        self.robot.a4x = 126.2
        self.robot.a5x = 64.1
        self.robot.a6x = 169

        self.acc = 10000  # Acurray of the angles sent to the arduino.
        self.num_joints = 6
        self.angles = [Angle(0, "rad") for _ in range(self.num_joints)]
        self.tool = 100
        self.arduino_angles = [0 for _ in range(self.num_joints)]
        self.is_homed = False

        self.coms_lock = threading.Lock()

        self.filem = FileManager()

        self.monitor = SerialMonitor(self,port,baudrate)

    
    def run_file(self,file_name):
        """Selects a file to read instructions from, sets self.cur_file. Every instruction is run by the method step()

        Args:
            file_name (str): name of the file where the instructions are stored.
        """
        self.filem.run_file(file_name)

    

    def step(self):
        """Makes the robot arm take a current step (read a new line from self.cur_file and run it.)

        Returns:
            bool: Ture if the file has lines left, false otherwise.
        """
        instruct = self.filem.step()

        if(instruct is None):
            return False

        if(type(instruct) is CordAngleInstruction):

            config = instruct.as_config()
            angles = self.robot.inverse_kinematics(config)
            assert angles != None, f"Config that failed: cords: {config.cords} and angles: {config.euler_angles}"
            self.move_to_angle_config(angles)
        
        if(type(instruct) is ToolAngleInstruction):
            tool = instruct.value
            self.move_gripper_to(tool)

        return True

    

    def update_arduino_angles(self, angles):
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
        return [Angle(x/self.acc, "rad") for x in self.arduino_angles]

    def send_command(self, command):
        """Sends a command to the arduino. Sends the command's message to the arduino.

        Args:
            command (Command): Calls the send method on a command, (sends it's message to the arduino)
        """
        self.monitor.send_command(command)
        
        
    def move_gripper_to(self,angle):
        """Moves the gripper to a certain angle configuration

        Args:
            angle (int): integer that represents the angle configuration of the gripper
        """
        if (self.tool == int(angle)):
            return None
        self.send_command(com.GripperCommand(self,int(angle)))
        self.tool = int(angle)
    
    def home_arm(self):
        """Homes all the joints of the arm (runs the home command)"""
        if not self.is_homed:
            print("\nHoming all joints!")
            self.send_command(com.HomeComand(self))
        
    def move_to_angle_config(self, angles):
        """Makes the robot go to a certain angle configuration (this is absolute positioning).

        Args:
            angles (list[Angles]): Angles to go to.
        """
        cur_angles = self.get_arduino_angles()
        dif = [Angle(fin.rad-ini.rad, "rad")
               for ini, fin in zip(cur_angles, angles)]

        if (all([abs(x.rad)<1/self.acc for x in dif])): #Check, so that only usefull commands are sent.
            return None
        command = com.MoveCommand(self, dif)
        self.send_command(command)

    def move_to_point(self, config):
        """Makes the tcp move to cords and certain euler angles. This is a point to point movement.

        Args:
            config (Config) : Point described as a config.
        """
        next_angles = self.robot.inverse_kinematics(config)
        if (next_angles is None):
            raise Exception("Angles out of reach.")
        self.move_to_angle_config(next_angles)
        self.move_gripper_to(config.tool)

    def gen_curve_points(self, points):
        """Generates curves ptp from a list of points

        Args:
            points (list[Config]): list of points   

        Returns:
            np.array: array with all the positions the tcp should follow
        """
        for i in range(len(points)-1):
            if (i == 0):
                result = self.generate_curve_ptp(points[i], points[i+1])
                continue
            result = np.append(result, self.generate_curve_ptp(
                points[i], points[i+1]), axis=0)
        return result

    def generate_curve_ptp(self, p1, p2, n=None):
        """Creates a parametric straight curve from point p1 to point p2.

        Args:
            p1 (Config): starting point
            p2 (Config): ending point
            n (int) : Number of points in the curve (definition)

        Returns:
            np.array: Array with all the positions to achieve the curve.
            (Dimensions: (self.numJoints+1),n)
        """
        cords_ini, euler_ini = p1.cords,p1.euler_angles
        cords_fin, euler_fin = p2.cords,p2.euler_angles
        tool_ini,tool_fin = p1.tool,p2.tool
        cords_ini = np.array(cords_ini)
        cords_fin = np.array(cords_fin)
        euler_ini = np.array([angle.rad for angle in euler_ini])
        euler_fin = np.array([angle.rad for angle in euler_fin])
        if (n == None):
            dist1 = np.linalg.norm(cords_ini-cords_fin)
            dist2 = np.linalg.norm(euler_ini-euler_fin)*60
            dist = max(dist1,dist2,1/5)
            n = int(dist*1.5)
        t = 0
        if (n ==0): #This means only the tool was changed
            n = abs(tool_ini-tool_fin)
        step = 1/n
        result = np.zeros((n+1, 7))
        for i in range(n+1):
            cur_cords = cords_ini * (1-t) + cords_fin*(t)
            cur_tool =  tool_ini * (1-t) + tool_fin*(t) 
            cur_euler = euler_ini*(1-t) + euler_fin*(t)
            cur_config = Config(cur_cords,[Angle(angle,"rad") for angle in cur_euler],cur_tool)
            assert self.robot.inverse_kinematics(cur_config) != None
            cur_post = np.append(cur_cords, cur_euler, axis=0)
            cur_post= np.append(cur_post,np.array([cur_tool]),axis=0)
            cur_post = np.transpose(cur_post)
            t += step
            result[i] += cur_post
        return result
