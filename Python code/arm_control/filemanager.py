import os
import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__author__ = "Alberto Abarzua"

class FileManager():
    """FileManger class, used to create and read positions scripts of the arm.
    """
    def __init__(self) -> None:
        self.files = os.listdir("data/")


                


    

