import numpy as np
import math
from numpy.lib.function_base import angle
import serial
import time
import filemanager 
#-----------------------------------------------------------
#-----------------------------------------------------------------------------------
# ANGLE CLASS SO THAT I DONT GET CONFUSED
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
class Angle:
    def __init__(self,angle,id) -> None:
        self.id = id
        if id == "rad":
            self.rad = angle
            self.deg = (180/np.pi)*angle
            self.step = (angle*1600)/(2*np.pi)
        if id == "deg":
            self.deg = angle
            self.rad = (np.pi/180)*angle
            self.step = (angle*1600)/(360)
        if id == "step":
            self.step = angle
            self.deg = (angle*360)/1600
            self.rad = (angle*2*np.pi)/1600
    def near2pi(self,n):
        new = n.rad
        prev = self.rad
        currentDist = abs(prev-new)
        (minDist,minValue) = currentDist, new
        for i in range(-2,3):
            thisDist = abs(prev - new -i*2*np.pi)
            if thisDist<minDist:
                minValue = new + i*2*np.pi
        return minValue
#--------------------------------------------
#-----------------------------------------------------------------------------------
# ROTATION AND TRANSLATION MATRIXES
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def rad2degree(angle):
    return (180/np.pi)*angle
def degree2rad(angle):
    return (np.pi/180)*angle
def xmatrix(angle):
    R = np.array([
        [1,0,0],
        [0,math.cos(angle),-math.sin(angle)],
        [0,math.sin(angle),math.cos(angle)]
    ])
    return R
def ymatrix(angle):
    R = np.array([
        [math.cos(angle),0,math.sin(angle)],
        [0,1,0],
        [-math.sin(angle),0,math.cos(angle)]
    ])
    return R

def zmatrix(angle):
    R  = np.array([
        [math.cos(angle),-math.sin(angle),0],
        [math.sin(angle),math.cos(angle),0],
        [0,0,1]
    ])
    return R
def tmatrix(R,D):
    T = np.block([
        [R,D],
        [0,0,0,1]
    ])
    return T


def rotationMatrixToEulerAngles(R):
    if (R[2,0] !=1 and R[2,0] !=-1):
        B1 = -math.asin(R[2,0])
        B2 = np.pi + B1
        A1 = math.atan2(R[2,1]/math.cos(B1),R[2,2]/math.cos(B1))
        A2 = math.atan2(R[2,1]/math.cos(B2),R[2,2]/math.cos(B2))
        C1 = math.atan2(R[1,0]/math.cos(B1),R[0,0]/math.cos(B1))
        C2 =math.atan2(R[1,0]/math.cos(B2),R[0,0]/math.cos(B2))
        return [float(A1),float(B1),float(C1)]
    else:
        C = 0
        if (R[2,0] ==-1):
            B = np.pi/2.0
            A = C+ math.atan2(R[0,1],R[0,2])
        else:
            B = -np.pi/2.0
            A = -C + math.atan2(-R[0,1],-R[0,2])
        return [float(A),float(B),float(C)]

def eulerAnglesToRotMatrix(A,B,C):
    return zmatrix(C)@ymatrix(B)@xmatrix(A)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# ROBOT ARM CLASS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

class RobotArm:

    
    def __init__(self,port,baudrate) -> None:
            # PARAMETROS FISICOS
        #J1
        self.a1x = 0
        self.a1y = 0
        self.a1z = 0
        #J2
        self.a2x = 0
        self.a2y = 0
        self.a2z = 0
        #J3
        self.a3x = 0
        self.a3y = 0
        self.a3z = 0
        #J4
        self.a4x = 0
        self.a4y = 0
        self.a4z = 0
        #J5
        self.a5x = 0
        self.a5y = 0
        self.a5z = 0
        #J6
        self.a6x = 0
        self.a6z = 0
        self.a6y = 0
        #Arduino pyserial
        self.arduino = serial.Serial()
        #Joints angles
        self.angles = [None,None,None,None,None,None]
        self.cords = [0.0,0.0,0.0,0.0,0.0,0.0]
        #File manager
        self.filem = filemanager.FileManager()
        self.arduino.port = port
        self.arduino.baudrate = baudrate
        self.arduino.open()
        
        self.isHomed = False
        self.gripper = 90
        self.updateAngles()
        self.getGripper()
        self.updateCords()

    def printinfo(self):
        self.updateCords()
        steps = [x.step for x in self.angles]
        print("ANGLES IN STEPS:",steps)
        print("CORDS X,Y,Z,A,B,C:",self.cords)
    def checkAngles(self):
        print("self.angles",[round(x.step,2) for x in self.angles],end = " ")
        print(self.callForAngles(),end = " ")
        print("griper",self.gripper)
    def check(self):
        self.updateCords()
        calledAngles = self.callForAngles()
        dk = self.directKinematics(self.angles)
        print("A:",[round(x.deg,2) for x in self.angles],end = " ")
        print("DK",[round(dk[i],2) for i in range(0,3)] + [round(dk[i].deg,2) for i in range(3,len(dk))],"IK:",[round(x.deg,2) for x in self.inverseKinematics(dk)])
        

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# FORWARD KINEMATCIS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
    def directKinematics(self,a):
        if (type(a[3]) != Angle) or (type(a[4]) != Angle) or (type(a[5]) != Angle):
            raise Exception("Angles not in 'Angle' dtype ")
        J1 = a[0].rad
        J2 = a[1].rad
        J3 = a[2].rad
        J4 = a[3].rad
        J5 = a[4].rad 
        J6 = a[5].rad
        ## BASE --> J1
        R1 = zmatrix(J1)
        D1 = np.array([
            [self.a1x],
            [self.a1y],
            [self.a1z]
        ])
        T1 = tmatrix(R1,D1)
        ## J1 -->  J2
        R2 = ymatrix(J2)
        D2 = np.array([
            [self.a2x],
            [self.a2y],
            [self.a2z]
        ])
        T2 = tmatrix(R2,D2)
        ## J2 -->  J3
        R3 = ymatrix(J3)
        D3 = np.array([
            [self.a3x],
            [self.a3y],
            [self.a3z]
        ])
        T3 = tmatrix(R3,D3)
        ## J3 -->  J4

        R4= xmatrix(J4)
        D4 = np.array([
            [self.a4x],
            [self.a4y],
            [self.a4z]
        ])
        T4 = tmatrix(R4,D4)
        ## J4 -->  J5
        R5= ymatrix(J5)
        D5 = np.array([
            [self.a5x],
            [self.a5y],
            [self.a5z]
        ])
        T5 = tmatrix(R5,D5)
        ## J5 -->  J6
        R6= xmatrix(J6)
        D6 = np.array([
            [self.a6x],
            [self.a6y],
            [self.a6z]
        ])
        T6 = tmatrix(R6,D6)
        ## Base--> TCP
        position = T1@T2@T3@T4@T5@T6@np.array([[0],[0],[0],[1]])
        rotation = R1@R2@R3@R4@R5@R6
        x = rotationMatrixToEulerAngles(rotation)
        result = []
        for elem in x:
            result.append(Angle(elem,"rad"))
        return list(position[:3,0])+result
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# INVERSE KINEMATICS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
    def inverseKinematics(self,l):
        if (type(l[3]) != Angle) or (type(l[4]) != Angle) or (type(l[5]) != Angle):
            raise Exception("Angles not in 'Angle' dtype ")
        x = l[0]
        y = l[1]
        z = l[2]
        A = l[3].rad
        B = l[4].rad
        C = l[5].rad
 
        TCP = np.array([
            [x],
            [y],
            [z]
        ])
        xdirection = eulerAnglesToRotMatrix(A,B,C) @ np.array([[1],[0],[0]])
        WP = TCP - self.a6x*xdirection
        # Finding J1,J2,J3

        J1 = Angle(math.atan2(WP[1,0],WP[0,0]),"rad")
        if (WP[0,0] == 0 and WP[1,0] == 0):
            J1 = Angle(degree2rad(self.angles[0]),"rad") ## Singularity, if Wx = Wy =0 dejar J1 como pos actual.
        WPxy = math.sqrt(WP[0,0]**2 + WP[1,0]**2)
        L = WPxy - self.a2x
        H = WP[2,0] - self.a1z-self.a2z
        P = math.sqrt(H**2 + L**2)
        b4x = math.sqrt(self.a4z**2+(self.a4x + self.a5x)**2)
        if (P<=self.a3z + b4x) and abs(self.a3z-b4x)<P:
            alfa = math.atan2(H,L)
            cosbeta =( P**2 + self.a3z**2 - b4x**2)/(2*P*self.a3z)
            beta = math.atan2(math.sqrt(1-cosbeta**2),cosbeta)
            cosgamma = (self.a3z**2  + b4x**2 - P**2)/(2*self.a3z*b4x)
            gamma = math.atan2(math.sqrt(1-cosgamma**2),cosgamma)
            lamb2 = math.atan2(self.a3x,self.a3z)
            delta = math.atan2(self.a4x+self.a5x,self.a4z)
            J2 = Angle(np.pi/2.0 - alfa  - beta,"rad")
            J3 = Angle(np.pi - gamma - delta,"rad")
            # Finding Wrist Orientation
            R1 = zmatrix(J1.rad)
            R2 = ymatrix(J2.rad)
            R3 = ymatrix(J3.rad)
            Rarm = R1@R2@R3
            Rarmt = Rarm.transpose()
            R = eulerAnglesToRotMatrix(A,B,C)
            Rwrist=Rarmt@R
            #Finding J4
            J5 = Angle(math.atan2(math.sqrt(1-Rwrist[0,0]**2),Rwrist[0,0] ),"rad")
            if J5.rad == 0:
                J6 = self.angles[5]
                J4 = Angle(math.atan2(Rwrist[2,1],Rwrist[2,2]),"rad")
            else:
                J4 = Angle(math.atan2(Rwrist[1,0],-Rwrist[2,0]),"rad")
                J6 = Angle(math.atan2(Rwrist[0,1],Rwrist[0,2]),"rad")
            preangle = [J1,J2,J3,J4,J5,J6]
            return preangle
 

    def updateCords(self) -> None:
        self.cords = self.directKinematics(self.angles)

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# COMS TO ARDUINO
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------  
    # Lee lineas de la comunicacion serial con arduino
    def read(self) -> str: 
        return self.arduino.readline().decode()
    # Pausa el programa hasta que el arduino esta listo para recibir info.
    def wait(self) -> None:
        while(self.read() != "0\n"):
            time.sleep(0.00001)


    # Pide los angulos (en steps) al arduino, y actualiza los valores de self.angles()
    def updateAngles(self) -> None: 
        self.wait()
        c = "i\n"
        self.arduino.write(c.encode())
        r = self.read()
        a = [float(x) for x in r.split(";")[:-1]]
        a.pop(1)
        #print(a)
        self.angles = [Angle(x,"step") for x in a]
        
    def callForAngles(self):
        self.wait()
        c = "i\n"
        self.arduino.write(c.encode())
        r = self.read()
        a = [float(x) for x in r.split(";")[:-1]]
        a.pop(1)
        #print(a)
        return a

    # Recibe una lista con angulos (en formato steps 1600 steps == 360 grad)
    def moveCommand(self,plist) -> None:
        self.wait()
        command = ""
        idx = 0
        end = " "
        for i in range(len(plist)):
            if i == (len(plist))-1:
                end = ""
            if i == 2:
                idx+=1
            command += "t" + str(idx) + " " + str(int(plist[i])) + end 
            idx +=1
        command += "\n"
        #print("command sent :",command)
        for i in range(len(self.angles)):
            self.angles[i] = Angle(self.angles[i].step + plist[i],"step") #Updating self.angles
        self.arduino.write(command.encode())

    # Realiza home a joint especifico
    def homeJoint(self,joint) -> None:
        self.wait()
        c = "h{}".fomat(joint)
        self.arduino.write(c.encode())
    
    # Pide el estado acual del gripper (formato grados de servo)
    def getGripper(self) -> float:
        self.wait()
        c = "r\n"
        self.arduino.write(c.encode())
        x = float(self.read())
        self.gripper = x

    # Manda por serial comando par mover el gripper (recibe pos en grados (0-180))
    def gripperCommand(self,pos):
        self.wait()
        c = "g0 {}\n".format(pos)
        self.gripper += pos # updating gripper angle
        self.arduino.write(c.encode())
    def callHoming(self):
        idx = 6
        for i in range(len(self.angles)): #6 5 4 3 1 0
            self.wait()
            if i ==4:
                idx -=1
            c = "h{}\n".format(idx)
            self.arduino.write(c.encode())
            
            idx -=1
            time.sleep(1)
        print("Finished homing all joints")
        self.isHomed = True
        self.updateAngles()



#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# MOVEMENT
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------  

    # Segun los angulos actuales, retorna una lista con cordenadas y angulos euler de la forma
    # [x,y,z,A,B,C]
    def currentPos(self) -> list:
        self.updateAngles()
        return self.directKinematics(self.angles)

    # Recibe coordenadas y angulos euler y realiza los comandos para alcanzar esta nueva posicion.
    def moveToPoint(self,l):
        newAngles= self.inverseKinematics(l)
        
        toMove = []
        for i in range(len(self.angles)):
            toMove.append(newAngles[i].step - self.angles[i].step)
        self.moveCommand(toMove)
    def moveToAngles(self,new):
        
        current = [x.step for x in self.angles]
        c  = []
        for i in range(len(new)):
            c.append(int(new[i]) - int(current[i]))
        #print(current,new,c)
        self.moveCommand(c) 

    # Recibe angulo del gripper y lo mueve a este.
    def moveToPointGripper(self,point):
        current = self.gripper
        self.gripperCommand(int(point) - int(current))


    # Lee un archivo y ejecuta todos los comandos en este linea por linea
    def runFile(self,filename):
        #self.callHoming()
        toRun = self.filem.readFile(filename)
        #self.callHoming()
        for instruct in toRun:
            print("instruct,", instruct)
            if len(instruct) == 6:
                self.moveToAngles(instruct)
            else:
                self.moveToPointGripper(instruct[0])
    # Agrega un comando al final de archivo
    def addInstruct(self,filename,instruct):
        self.filem.addToFile(filename,instruct)

    
        

