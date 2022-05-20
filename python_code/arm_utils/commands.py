import enum

from torch import true_divide
from . import bins
import time
import threading
import numpy as np


import sys
import os.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_utils.armTransforms import Angle, OutOfBoundsError

__author__ = "Alberto Abarzua"


class Command:
    """Superclass for all the commands that can be sent to the arduino
    """

    def __init__(self, controller) -> None:
        """Command constructor, used to create a new commands. Receives the controller where it is used.

        Args:
            controller (Controller): Controller where the command will be used.
        """
        super().__init__()
        self.controller = controller

    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        raise NotImplementedError("This method is not implemented")
    def update(self):
        """Used to update the status of the controller.
        """
        pass

    def is_correct(self):
        """Checks if the command and it's values are correct

        Returns:
            bool: true if the command is correct, false otherwise.
        """
        return True
    def send(self):
        """Sends the message from this command to the arduino conected to controller.
        """
        self.update()
        self.controller.monitor.write(self.message.encode())

    def __str__(self):
        return str(self.message)

class MoveCommand(Command):
    """MoveCommand class, used to create a command from a list of angles. Subclass of Command.

    """

    def __init__(self, controller, angles):
        """Creates a new move command with certain angles

        Args:
            angles (list[Angle]): list of angles 
        """
        super().__init__(controller=controller)
        self.angles = angles
        self.rad_times_acc_angles = [
            str(round(angle.rad*self.controller.acc)) for angle in self.angles]
        self.angles_for_arduino = self.rad_times_acc_angles[:]

    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        
        command = bins.Message("m",1,self.rad_times_acc_angles)
        return command


    def send(self):
        """Sends the command to the controllers arduino.
        """
        super().send()

    def update(self):
        """Used to update the status of the controller.
        """
        self.controller.update_arduino_angles(
            [int(x) for x in self.angles_for_arduino])
        self.controller.robot.angles = self.controller.get_arduino_angles()
   
class GripperCommand(Command):
    """Class used to send a command to the robot's tool (gripper), not yet implemented.

    """
    def __init__(self, controller,angle) -> None:
        """GripperCommand used to move the robot't tool

        Args:
            controller (Controller): controller of the arm
            angle (int): interger between (85 and 170) representing the state of the gripper.
        """
        super().__init__(controller)
        self.angle = angle


    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        return bins.Message("g",1,[self.angle])

    def send(self):
        """Sends the command to the controllers arduino.
        """
        super().send()
    def update(self):
        """Used to update the status of the controller.
        """
        self.controller.tool = self.angle

    def is_correct(self):
        return self.angle in range(60,150)

class HomeComand(Command):
    """Command used to home the joints of the robot arm, gets the arm to it's home position"""
    def __init__(self, controller) -> None:
        super().__init__(controller)

    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        return  bins.Message('h',0)

    def send(self):
        """Sends the command to the controllers arduino.
        """
        super().send()
    def update(self):
        """Used to update the status of the controller.
        """
        self.controller.is_homed = True
        
