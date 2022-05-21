from ast import In
from dataclasses import astuple
import os
import os.path
import sys
from time import sleep
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from arm_utils.armTransforms import Angle
from arm_utils.armTransforms import Config
from arm_utils.commands import *
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


class ToolAngleInstruction(Instruction):
    """Tool angle instruction used to create instructons for the robot's tool

    Args:
        Instruction (_type_): _description_
    """

    def __init__(self, value) -> None:
        """Tool angle instruction,

        Args:
            value (int): angle of the tool to be stored.
        """
        super().__init__(value)
        if (type(value) is str):
            self.value = int(value[2:].strip())

    @property
    def line(self):
        """Gets the string representation of the instruction. Used to store the instruction in
        a file.

        Returns:
            str: string representation.
        """
        return "t {}\n".format(int(self.value))

class SleepInstruction(Instruction):
    def __init__(self, value) -> None:
        """Creates a new sleep instruction,

        Args:
            value (float): time in seconds to wait.
        """
        super().__init__(value)
        if (type(value) is str):
            self.value = float(value[2:].strip())
    @property
    def line(self):
        return "s {:.3f}\n".format(self.value)

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
            return Config(cords,angles,None)

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




class FileManager:
    """FileManger class, used to create and read positions scripts of the arm.
    """

    def __init__(self) -> None:
        """FileManager constructor
        """
        self.path = "arm_control/data/"
        self.files = os.listdir(self.path)
        self.cur_file = None

    def from_curve_to_instruct(self, curve,sleep_idxs =[]):
        """Receives an array of positions and returns a list of instructions.

        Args:
            curve (np.array): array with positions
        """

        result = []
        for i,elem in enumerate(curve):
            if i in sleep_idxs:
                result.append(SleepInstruction(1.0))
            cord = elem[:3]
            angle = [Angle(x, "rad") for x in elem[3:-1]]
            tool = elem[6]
            result.append(CordAngleInstruction(Config(cord,angle,tool)))
            result.append(ToolAngleInstruction(tool))
        return result

    def get_demo_number(self):
        """gets the max number that follows a file named demo in this.files.
        example : this.files = [demo1.txt,demo5.txt] -- > 6

        Returns:
            int: current demo number
        """
        nums = []
        self.files = os.listdir(self.path)
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
    def interrupt_file(self):
        """Closes the current file.
        """
        try:
            self.cur_file.close()
            self.cur_file = None
        except:
            print("File was already closed.")
            
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
            Instruction: Returns the current instruction read from cur_file.
        """
        if (self.cur_file == None or self.cur_file.closed):
            return None

        cur_line = self.cur_file.readline()
        if (cur_line == ""):
            self.cur_file.close()
            return False

        if (cur_line[0] == "c"):
            return  CordAngleInstruction(cur_line)

        if(cur_line[0] == "t"):
           return ToolAngleInstruction(cur_line)
        
        if(cur_line[0] == "s"):
            return SleepInstruction(cur_line)
            
