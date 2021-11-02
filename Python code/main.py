import robotarm
import pygame
import numpy as np
import math
import serial
import time


robot = robotarm.RobotArm("COM5",115200)
#J1
#J2
robot.a2x = 0
robot.a2z = 178
#J3
robot.a3z = 148+8
#J4
robot.a4x = 54
#J5
robot.a5x = 116
#J6
robot.a6x = 156
#robot.callHoming()

# COORDS TO MOVE TO
robot.updateCords()
toMove =  [x.step for x in robot.angles]
robot.updateCords()
toMoveCords = robot.cords

robot.getGripper()
grip = robot.gripper
pygame.init()
done = False
homed = False
z =0
x =0
clock = pygame.time.Clock()
pygame.joystick.init()

step = 7
step2 = 0.5
xyzMode = False
btimer = 0

# -------- Main Program Loop -----------
while not done:
    joystick_count = pygame.joystick.get_count()
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            pass
        elif event.type == pygame.JOYBUTTONDOWN:
            pass
        elif event.type == pygame.JOYBUTTONUP:
            pass

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        try:
            jid = joystick.get_instance_id()
        except AttributeError:
            jid = joystick.get_id()

        name = joystick.get_name()
        try:
            guid = joystick.get_guid()
        except AttributeError:
            pass
        else:
            pass

        #----- Axis config -----
        axes = joystick.get_numaxes()
        for i in range(axes):
            axis = joystick.get_axis(i)
            if i == 0 and abs(axis)>0.3: #j3
                if not xyzMode:
                    toMove[3] -= step*axis
                else:
                    toMoveCords[1] += step2*axis
         

            if i == 1 and abs(axis)>0.3: #j2
                if not xyzMode:
                    toMove[2] -= step*axis
                else:
                    toMoveCords[2] -= step2*axis

            if i == 2 and abs(axis)>0.3: #j5
                if not xyzMode:
                    toMove[5] -= step*axis
            
            if i == 3 and abs(axis)>0.3: #j4
                if not xyzMode:
                    toMove[4] -= step*axis
                else:
                    toMoveCords[4] = robotarm.Angle(toMoveCords[4].deg + step2*axis,"deg")

                    


            
            

        #----- buttons config -----
        buttons = joystick.get_numbuttons()
        for i in range(buttons):
            button = joystick.get_button(i)
            if i == 6 and button == 1:
                done = True
            if i == 2 and button ==1:
                #cambiamos de modo xyz a modo j1 j2 j3 j4
                print("learning mode, enter filename: ",robot.filem.files)
                filename  = input()
                


            if i == 1 and button ==1 and btimer == 0: #capture and write pos
                robot.updateCords()
                robot.addInstruct(filename,toMove)
                #robot.addInstruct(filename,robot.cords[:3] + [robot.cords[i].step for i in range(3,len(robot.cords))])
                robot.addInstruct(filename,[robot.gripper])
                btimer = 100
            if i ==4 and button: #grip +
                grip += 10
            if i ==5 and button:#grip -
                
                grip -= 10
            if i == 3 and button:
                if xyzMode:
                    toMoveCords[5] = robotarm.Angle(toMoveCords[5].deg + step2,"deg")
                print("run file:" , robot.filem.files)
                x = input()
                robot.runFile(x)

            if i == 0 and button:
                if xyzMode:
                    toMoveCords[5] = robotarm.Angle(toMoveCords[5].deg - step2,"deg")
                
            if i == 7 and button:
                print("homing")
                robot.callHoming()
                toMove = [x.step for x in robot.angles]
                robot.updateCords()
                toMoveCords = robot.cords
                homed = True
            if i == 8 and button:
                homed = True
                toMove = [x.step for x in robot.angles]
            
            
            


        #----- dpad config -----
        hats = joystick.get_numhats()
        for i in range(hats):
            hat = joystick.get_hat(i)
            if hat == (0,1): #up
                if not xyzMode:
                    toMove[1]+=step*0.2 #+j1
                else:
                    toMoveCords[0] += step2
            if hat ==(0,-1): # down
                if not xyzMode:
                    toMove[1]-=step*0.2 #-j1
                else:
                    toMoveCords[0] -= step2

            if hat == (-1,0): # left
                if not xyzMode:
                    toMove[0] +=step # +j0
                else:
                    toMoveCords[3] = robotarm.Angle(toMoveCords[3].deg - step2,"deg")
            if hat == (1,0): # right
                if not xyzMode:
                    toMove[0] -=step # -j0
                else:
                    toMoveCords[3] = robotarm.Angle(toMoveCords[3].deg + step2,"deg")
    '''
    for i in range(0,3):
        toMove[i] = round(toMove[i],4)
    print("toMove",toMove[:3] + [round(toMove[i].deg,4) for i in range(3,len(toMove))],end = "")
    
    '''
    #print(type(toMove[5]),toMove, end =" ")
    #robot.check()
    
    
    
    #print(robot.gripper)
    if not xyzMode:
        robot.moveToAngles(toMove)
        print([x.deg for x in robot.angles],end = " \n")
    if xyzMode:
        
        robot.moveToPoint(toMoveCords)
        print(toMoveCords[:3] + [toMoveCords[i].deg for i in range(3,len(toMoveCords))])
    
    #robot.check()   
    #robot.updateCords() 
    robot.moveToPointGripper(grip)
    if btimer>0:
        btimer -=1
pygame.quit()