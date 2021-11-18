import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from numpy.lib.function_base import angle
import serial
import time
from arm_utils.armTransforms import *

__author__ = "Alberto Abarzua"


class RobotArm:
    """RobotArm class, used to create and calculate the kinematics of a robot arm.
    """

    def __init__(self) -> None:
        """Robot arm constructor, it creates the robot arm with it's physical parameters and 
        initializes with all the angles equal to zero.
        """
        # Physical parameters
        # J1
        self.a1x = 0
        self.a1y = 0
        self.a1z = 0
        # J2
        self.a2x = 0
        self.a2y = 0
        self.a2z = 0
        # J3
        self.a3x = 0
        self.a3y = 0
        self.a3z = 0
        # J4
        self.a4x = 0
        self.a4y = 0
        self.a4z = 0
        # J5
        self.a5x = 0
        self.a5y = 0
        self.a5z = 0
        # J6
        self.a6x = 0
        self.a6z = 0
        self.a6y = 0

        # Joints angles
        self.angles = [Angle(0, "rad") for i in range(6)]
        # Position x,yz
        self.xyz = None
        # Euler Angles
        self.euler_angles = None


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# FORWARD KINEMATCIS
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

    def direct_kinematics(self, angles=None):
        """Direct Kinematics function,takes a configuration of angles for all the robots joints and 
        calculates the current position of the Arms tool and it's euler angles. If the list
        of angles is not provided direct_kinematics will use the robots current angles.

        Args:
            angles (Angle, optional): list of Angles to use as robot config. Defaults to None.

        Returns:
            tuple(list[float],list[Angle]): returns the current position of the tool and the current euler angles
            as follows: ([x,y,z],[A,B,C])
        """
        if (angles == None):
            angles = self.angles
        J1, J2, J3, J4, J5, J6 = angles
        # BASE --> J1
        R1 = zmatrix(J1)
        D1 = np.array([
            [self.a1x],
            [self.a1y],
            [self.a1z]
        ])
        T1 = tmatrix(R1, D1)
        # J1 -->  J2
        R2 = ymatrix(J2)
        D2 = np.array([
            [self.a2x],
            [self.a2y],
            [self.a2z]
        ])
        T2 = tmatrix(R2, D2)
        # J2 -->  J3
        R3 = ymatrix(J3)
        D3 = np.array([
            [self.a3x],
            [self.a3y],
            [self.a3z]
        ])
        T3 = tmatrix(R3, D3)
        # J3 -->  J4

        R4 = xmatrix(J4)
        D4 = np.array([
            [self.a4x],
            [self.a4y],
            [self.a4z]
        ])
        T4 = tmatrix(R4, D4)
        # J4 -->  J5
        R5 = ymatrix(J5)
        D5 = np.array([
            [self.a5x],
            [self.a5y],
            [self.a5z]
        ])
        T5 = tmatrix(R5, D5)
        # J5 -->  J6
        R6 = xmatrix(J6)
        D6 = np.array([
            [self.a6x],
            [self.a6y],
            [self.a6z]
        ])
        T6 = tmatrix(R6, D6)
        # Base--> TCP
        position = T1@T2@T3@T4@T5@T6@np.array([[0], [0], [0], [1]])
        rotation = R1@R2@R3@R4@R5@R6
        euler_angles = rotationMatrixToEulerAngles(rotation)
        pos = list(position[:3, 0])
        self.xyz = pos
        self.euler_angles = euler_angles
        return pos, euler_angles
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# INVERSE KINEMATICS
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------

    def inverse_kinematics(self, config=None):
        """Gets the angles that the robots joints should have so that the tool is in the position and
        euler angles given by config. If config is None the current config of the robot arm is used.

        Args:
            config (tuple(list[float],list[Angle]), optional): [description]. Defaults to None.

        Returns:
            list[Angle]: list of Angles the robot arm should have to reach config.
        """
        prev = self.angles[:
                           ]  # Current angles of the robot (used to choose the closest angles to achieve config)
        if (config == None):
            config = self.xyz, self.euler_angles
        xyz, euler_angles = config
        x, y, z = xyz
        A, B, C = euler_angles

        TCP = np.array([
            [x],
            [y],
            [z]
        ])
        xdirection = eulerAnglesToRotMatrix(
            A, B, C) @ np.array([[1], [0], [0]])
        WP = TCP - self.a6x*xdirection
        # Finding J1,J2,J3

        J1 = Angle(np.arctan2(WP[1, 0], WP[0, 0]), "rad")
        if (WP[0, 0] == 0 and WP[1, 0] == 0):
            # Singularity, if Wx = Wy =0 dejar J1 como pos actual.
            J1 = self.angles[0]
        WPxy = np.sqrt(WP[0, 0]**2 + WP[1, 0]**2)
        L = WPxy - self.a2x
        H = WP[2, 0] - self.a1z-self.a2z
        P = np.sqrt(H**2 + L**2)
        b4x = np.sqrt(self.a4z**2+(self.a4x + self.a5x)**2)
        if (P <= self.a3z + b4x) and abs(self.a3z-b4x) < P:
            alfa = np.arctan2(H, L)
            cosbeta = (P**2 + self.a3z**2 - b4x**2)/(2*P*self.a3z)
            beta = np.arctan2(np.sqrt(1-cosbeta**2), cosbeta)
            cosgamma = (self.a3z**2 + b4x**2 - P**2)/(2*self.a3z*b4x)
            gamma = np.arctan2(np.sqrt(1-cosgamma**2), cosgamma)
            lamb2 = np.arctan2(self.a3x, self.a3z)
            delta = np.arctan2(self.a4x+self.a5x, self.a4z)
            J2 = Angle(np.pi/2.0 - alfa - beta, "rad")
            J3 = Angle(np.pi - gamma - delta, "rad")
            # Finding Wrist Orientation
            R1 = zmatrix(J1)
            R2 = ymatrix(J2)
            R3 = ymatrix(J3)
            Rarm = R1@R2@R3
            Rarmt = Rarm.transpose()
            R = eulerAnglesToRotMatrix(A, B, C)
            Rwrist = Rarmt@R
            # Finding J4
            J5 = Angle(np.arctan2(
                np.sqrt(1-Rwrist[0, 0]**2), Rwrist[0, 0]), "rad")
            if J5.rad == 0:  # Singularity
                J4 = self.angles[5]
                J6 = Angle(np.arctan2(
                    Rwrist[2, 1], Rwrist[2, 2]), "rad").sub(J4)
            else:
                J4 = Angle(np.arctan2(Rwrist[1, 0], -Rwrist[2, 0]), "rad")
                J6 = Angle(np.arctan2(Rwrist[0, 1], Rwrist[0, 2]), "rad")
            angles = [J1, J2, J3, J4, J5, J6]
            return nearest_to_prev([J1, J2, J3, J4, J5, J6], prev)
