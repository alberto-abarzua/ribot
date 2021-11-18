import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import arm_control.commands as com
import arm_utils.robotarm as robotarm
from arm_utils.armTransforms import Angle
import time
import serial
from arm_control.arduino_dummy import DummyArduino
from arm_control.filemanager import CordAngleInstruction, FileManager

from serial.serialutil import SerialException


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
        if (port is None or baudrate is None):  # Used during testing.
            self.arduino = DummyArduino()
        else:
            self.arduino = serial.Serial(baudrate=baudrate, port=port)
            if not self.arduino.isOpen():
                try:
                    self.arduino.open()
                except SerialException as e:
                    print("Error opening serial port: " + str(e))
        time.sleep(0.5)
        # Robot arm initialization

        self.robot = robotarm.RobotArm()

        # Physical paramters in mm.
        self.robot.a2x = 0
        self.robot.a2z = 178
        self.robot.a3z = 156
        self.robot.a4x = 54
        self.robot.a5x = 116
        self.robot.a6x = 156

        self.acc = 10000  # Acurray of the angles sent to the arduino.
        self.num_joints = 6
        self.angles = [Angle(0, "rad") for _ in range(self.num_joints)]
        self.arduino_angles = [0 for _ in range(self.num_joints)]

        self.filem = FileManager()
        self.cur_file = None

    def run_file(self, file_name):
        """Selects a file to read instructions from, sets self.cur_file. Every instruction is run by the method step()

        Args:
            file_name (str): name of the file where the instructions are stored.
        """
        try:
            self.cur_file = open(file_name, "r")
        except Exception as e:
            print("Error opening file: " + str(e))

    def step(self):
        """Makes the robot arm take a current step (read a new line from self.cur_file and run it.)

        Returns:
            bool: Ture if the file has lines left, false otherwise.
        """
        if (self.cur_file == None or self.cur_file.closed):
            return False
        cur_line = self.cur_file.readline()
        if (cur_line == ""):
            self.cur_file.close()
            return False

        if (cur_line[0] == "c"):
            instruct = CordAngleInstruction(cur_line)
            cords, angle = instruct.as_tuple()
            angles = self.robot.inverse_kinematics((cords, angle))
            assert angles != None, f"Config that failed: cords: {cords} and angles: {angle}"
            self.move_to_angle_config(angles)

        return True

    def read(self):
        """Read a line from the arduino.

        Returns:
            str: decoded line read from the arduino
        """
        if (self.arduino.in_waiting > 2):
            val = self.arduino.readline()
            try:
                val.decode()
            except Exception as e:
                print(str(e), "value that caused the error: ", val)
                return None
            return val.decode().strip()
        return None

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
        self.wait()
        command.send()

    def wait(self):
        """Runs a sleep timer until the arduino is ready to receive more data.
        """
        while(self.read() != "1"):
            time.sleep(0.00001)

    def move_to_angle_config(self, angles):
        """Makes the robot go to a certain angle configuration (this is absolute positioning).

        Args:
            angles (list[Angles]): Angles to go to.
        """
        cur_angles = self.get_arduino_angles()
        dif = [Angle(fin.rad-ini.rad, "rad")
               for ini, fin in zip(cur_angles, angles)]
        command = com.MoveCommand(self, dif)
        self.send_command(command)

    def move_to_point(self, cords, angles):
        """Makes the tcp move to cords and certain euler angles. This is a point to point movement.

        Args:
            cords (list[int]): list x,y,z coords of the tcp to reach
            angles (list[Angle]): euler angles the tcp should have.
        """
        next_angles = self.robot.inverse_kinematics((cords, angles))
        if (next_angles is None):
            return "Angles out of reach"
        self.move_to_angle_config(next_angles)

    def gen_curve_points(self, points):
        """Generates curves ptp from a list of points

        Args:
            points (list[tuple[List[float],List[Angle]]]): list of points   

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

        Both points should follow the next syntax:
        p = ([x,y,z],[A,B,C])

        Args:
            p1 (tuple[List[float],List[Angle]]): starting point
            p2 (tuple[List[float],List[Angle]]): ending point
            n (int) : Number of points in the curve (definition)

        Returns:
            np.array: Array with all the positions to achieve the curve.
            (Dimensions: (self.numJoints+1),n)
        """
        cords_ini, euler_ini = p1
        cords_fin, euler_fin = p2
        cords_ini = np.array(cords_ini)
        cords_fin = np.array(cords_fin)
        euler_ini = np.array([angle.rad for angle in euler_ini])
        euler_fin = np.array([angle.rad for angle in euler_fin])
        if (n == None):
            dist1 = np.linalg.norm(cords_ini-cords_fin)
            dist2 = np.linalg.norm(euler_ini-euler_fin)*100
            dist = max(dist1,dist2,1/5)
            n = int(dist)*5
        result = np.zeros((n+1, 6))
        t = 0
        step = 1/n
        for i in range(n+1):
            cur_cords = cords_ini * (1-t) + cords_fin*(t)
            cur_euler = euler_ini*(1-t) + euler_fin*(t)
            assert(self.robot.inverse_kinematics(
                (cur_cords, [Angle(x, "rad") for x in cur_euler])) != None)
            cur_post = np.append(cur_cords, cur_euler, axis=0)
            cur_post = np.transpose(cur_post)
            t += step
            result[i] += cur_post
        return result
