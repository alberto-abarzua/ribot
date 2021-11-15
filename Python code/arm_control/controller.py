#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# COMS TO ARDUINO
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------  


class Controller():

    

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

    
        

