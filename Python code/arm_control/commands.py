from . import bins

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

    def send(self):
        """Sends the message from this command to the arduino conected to controller.
        """
        self.controller.arduino.write(self.message.encode())


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

    @property
    def message(self):
        """Generates the message that will be sent to the arduino

        Returns:
            Message: message to the arduino to do this command
        """
        rad_times_acc_angles = [
            str(round(angle.rad*self.controller.acc)) for angle in self.angles]
        self.angles_for_arduino = rad_times_acc_angles[:]
        command = bins.Message("m",1,rad_times_acc_angles)
        return command

    def send(self):
        """Sends the command to the controllers arduino.
        """
        super().send()
        # Keep track of the angles sent.
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
        
