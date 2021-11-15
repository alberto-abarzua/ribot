import os
import os.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arm_utils.robotarm
import time

class FileManager():
    def __init__(self) -> None:
        self.files = os.listdir("data/")

    def cord2code(self,cords):
        m = [str(int(x)) for x in cords]
        return "c " + " ".join(m) + "\n"
    def code2list(self,code):
        x = code[2:-1].split(" ")
        '''
        if len(x)==6 and type(x[5]) != ):
            return [float(y) for y in x[:3]] + [robotarm.Angle(float(x[i]),"step")  for i in range(3,len(x)) ]
            '''
        return [float(y) for y in x]
    
    def gripper2code(self,angle):
        if type(angle) == list:
            angle = angle[0]
        return "g " + str(angle) + "\n"
    
    
    def writeNewFile(self,list,filename):
        file = open("data/" +filename,"w")
        toWrite = []
        for item in list:
            if len(item) == 6:
                toWrite.append(self.cord2code(item))
            else:
                toWrite.append(self.gripper2code(item))
        file.writelines(toWrite)
        file.close()
    def readFile(self,filename):
        file = open("data/" + filename,"r")
        lines = file.readlines()
        result = [self.code2list(x) for x in lines]
        file.close()
        return result
    def addToFile(self,filename,line):
        file = open("data/" + filename,"a")
        if len(line) == 6:
            file.write(self.cord2code(line))
        else:
            file.write(self.gripper2code(line[0]))
        file.close()

                


    

