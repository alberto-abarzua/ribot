from dataclasses import astuple
import os
import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_utils.armTransforms import Angle
from arm_utils.armTransforms import Config

__author__ = "Alberto Abarzua"


class Instruction:
    """Superclass for all the instructions that can be stored in a file.
    """

    def __init__(self, value) -> None:
        """Instruction constructos, receives a value that represents this instruction.

        Args:
            value (any): value of the instruction
        """
        self.value = value

    @property
    def line(self):
        """Gets the string representation of the instruction. Used to store the instruction in
        a file.

        Returns:
            str: string representation.
        """
        raise NotImplementedError("This method is not implemented")


class CordAngleInstruction(Instruction):
    """Used to store in a file a position and angles for the tcp
    """

    def __init__(self, value):
        """Constructor, receives a value that represents a coordinate and euler angle configuration.
        Can receive the string representation stored in files and a tuple ([x,y,z],[a,b,c]).
        String representation example:
            "c x y z a b c" -- > "c 300 0 300 0 0 0"

        Args:   
            value (tuple[List[float],List[Angle]] or str): value that represents a coordinate and angle config.
        """
        super().__init__(value)
        if (type(value) is str):
            self.value = value.strip()

    def as_config(self):
        """Gets the cords and angles of this instruction as a tuple (cords,angles)

        Returns:
            Config: position that describes this instruction
        """
        if (type(self.value) is str):
            l = [float(x) for x in self.value[2:].split(" ")]
            cords = l[:3]
            angles = [Angle(x, "rad") for x in l[3:]]
            return Config(cords,angles)

        return self.value

    @property
    def line(self):
        """Gets the string representation of the instruction. Used to store the instruction in
        a file.

        Returns:
            str: string representation.
        """
        if (type(self.value) is str):
            return self.value + "\n"
        cords, angles = self.value.cords,self.value.euler_angles
        result = [str(round(x, ndigits=5)) for x in cords] + \
            [str(round(x.rad, ndigits=8)) for x in angles]
        return "c " + " ".join(result) + "\n"


class FileManager():
    """FileManger class, used to create and read positions scripts of the arm.
    """

    def __init__(self) -> None:
        """FileManager constructor
        """
        self.path = "arm_control/data/"
        self.files = os.listdir(self.path)

    def from_curve_to_instruct(self, curve):
        """Receives an array of positions and returns a list of instructions.

        Args:
            curve (np.array): array with positions
        """
        result = []
        for elem in curve:
            cord = elem[:3]
            angle = [Angle(x, "rad") for x in elem[3:]]
            result.append(CordAngleInstruction(Config(cord,angle)))
        return result

    def get_demo_number(self):
        """gets the max number that follows a file named demo in this.files.
        example : this.files = [demo1.txt,demo5.txt] -- > 6

        Returns:
            int: current demo number
        """
        nums = []
        for elem in self.files:
            if ("demo" in elem):
                nums.append(int(elem[4:elem.index(".txt")]))
        return max(nums) + 1

    def write_file(self, instruct_sequence, filename):
        """Writes all the lines from a set of instructions on to a file

        Args:
            instruct_sequence (list[Insctruction]): list of instructions
            filename (str): name of the file where it will write the instructions
        """
        with open(self.path+filename, "w") as file:
            for elem in instruct_sequence:
                file.write(elem.line)
