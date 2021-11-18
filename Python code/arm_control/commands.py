class Command:
    """Superclass for all the commands that can be sent to the arduino
    """

    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

    @property
    def message(self):
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
        rad_times_acc_angles = [
            str(round(angle.rad*self.controller.acc)) for angle in self.angles]
        self.angles_for_arduino = rad_times_acc_angles[:]
        rad_times_acc_angles.insert(1, rad_times_acc_angles[1])
        command = "m{} ".format(self.controller.num_joints + 1)
        command += " ".join(rad_times_acc_angles)
        command += "\n"
        return command

    def send(self):
        super().send()
        # Keep track of the angles sent.
        self.controller.update_arduino_angles(
            [int(x) for x in self.angles_for_arduino])
        self.controller.robot.angles = self.controller.get_arduino_angles()


class GripperCommand(Command):
    """Class used to send a command to the robot's tool (gripper), not yet implemented.

    """
    pass
