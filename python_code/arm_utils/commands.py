
from . import bins
import time
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
        self.angles_rad = [x.rad for x in self.angles]
        self.rad_times_acc_angles = [
            str(round(angle.rad*self.controller.acc)) for angle in self.angles]
        self.angles_for_arduino = self.rad_times_acc_angles[:]

    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        
        command = bins.Message("m",1,self.angles_for_arduino)
        return command


    def send(self):
        """Sends the command to the controllers arduino.
        """
        super().send()


    def update(self):
        """Used to update the status of the controller.
        """
        angles_int = [int(x) for x in self.angles_for_arduino]
        self.controller.update_arduino_angles(angles_int)
        self.controller.robot.angles = self.controller.get_arduino_angles()
        if self.controller.enable_log:
            ratios = self.controller.robot.joint_ratios
            angles = angles_int
            micro_stepping = self.controller.micro_stepping
            acc = self.controller.acc
            values = []
            for ratio,angle in zip(ratios,angles):
                values +=[int((ratio*angle*100*micro_stepping)/(np.pi*acc))]
            self.controller.log(time.perf_counter(),values,self.angles_rad)
    

    def __str__(self):
        ratios = self.controller.robot.joint_ratios
        angles = [int(x) for x in self.angles_for_arduino]
        micro_stepping = self.controller.micro_stepping
        acc = self.controller.acc
        values = []
        for ratio,angle in zip(ratios,angles):
            values +=[(ratio*angle*100*micro_stepping)/(np.pi*acc)]
        return "m1_positions {:2f} {:2f} {:2f} {:2f} {:2f} {:2f}".format(*values)

        
   
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
        
