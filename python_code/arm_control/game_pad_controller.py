import sys
import os.path


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inputs import get_gamepad
import math
import threading
import time
from arm_control import filemanager
from arm_utils.armTransforms import Angle
class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        self.buttons = {
            "buttons" : 0,
            "LeftJoystickY" : 0,
            "LeftJoystickX" : 0,
            "RightJoystickY" : 0,
            "RightJoystickX" : 0,
            "LeftTrigger" : 0,
            "RightTrigger" : 0,
            "LeftBumper" : 0,
            "RightBumper" : 0,
            "A" : 0,
            "X" : 0,
            "Y" : 0,
            "B" : 0,
            "LeftThumb" : 0,
            "RightThumb" : 0,
            "Back" : 0,
            "Start" : 0,
            "LeftDPad" : 0,
            "RightDPad" : 0,
            "UpDPad" : 0,
            "DownDPad" : 0
            }

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()


    def read(self): 
        return self.buttons

    def clean_trigger(self,val):
        tolerance = 0.1
        pre = val/XboxController.MAX_TRIG_VAL
        if (abs(pre)<tolerance):
            return 0
        return pre
    def clean_joy(self,val):
        tolerance = 0.3
        pre = val/XboxController.MAX_JOY_VAL
        if (abs(pre)<tolerance):
            return 0
        return pre

    def _monitor_controller(self):
        while True:
            try:
                events = get_gamepad()

            except Exception as e:
                print(e)
                return
                
            for event in events:
                if event.code == 'ABS_Y':
                    self.buttons["LeftJoystickY"] = self.clean_joy(event.state)
                elif event.code == 'ABS_X':
                    self.buttons["LeftJoystickX"] = self.clean_joy(event.state) # normalize between -1 and 1
                elif event.code == 'ABS_RY':
                    self.buttons["RightJoystickY"] = self.clean_joy(event.state) # normalize between -1 and 1
                elif event.code == 'ABS_RX':
                    self.buttons["RightJoystickX"] = self.clean_joy(event.state) # normalize between -1 and 1

                elif event.code == 'ABS_Z':
                    self.buttons["LeftTrigger"] = self.clean_trigger(event.state)# normalize between 0 and 1
                elif event.code == 'ABS_RZ':
                    self.buttons["RightTrigger"] = self.clean_trigger(event.state)# normalize between 0 and 1
                elif event.code == 'BTN_TL':
                    self.buttons["LeftBumper"] = event.state
                elif event.code == 'BTN_TR':
                    self.buttons["RightBumper"] = event.state
                elif event.code == 'BTN_SOUTH':
                    self.buttons["A"] = event.state
                elif event.code == 'BTN_NORTH':
                    self.buttons["X"] = event.state
                elif event.code == 'BTN_WEST':
                    self.buttons["Y"] = event.state
                elif event.code == 'BTN_EAST':
                    self.buttons["B"] = event.state
                elif event.code == 'BTN_THUMBL':
                    self.buttons["LeftThumb"] = event.state
                elif event.code == 'BTN_THUMBR':
                    self.buttons["RightThumb"] = event.state
                elif event.code == 'BTN_SELECT':
                    self.buttons["Back"] = event.state
                elif event.code == 'BTN_START':
                    self.buttons["Start"] = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.buttons["LeftDPad"] = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.buttons["RightDPad"] = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.buttons["UpDPad"] = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.buttons["DownDPad"] = event.state



class ArmGamePad:

    def __init__(self,controller) -> None:
        self.joy = XboxController()
    
        self.buttons =self.joy.buttons
        self.controller = controller
        self.robot = self.controller.robot
        self.robot.direct_kinematics()  # We update the euler angles and xyz
        xyz,euler_angles = self.robot.config.cords,self.robot.config.euler_angles
        x, y,z = xyz
        A, B,C = euler_angles
        self.tool = 100
        self.dir_step = 70
        self.angle_step = 0.3
        self.fps = 10
        

    def run(self):
        t0 = time.perf_counter()
        sign = lambda x :math.copysign(1,x)
        while(True):
            t1 = time.perf_counter()
            dt = t1 - t0
            t0 = t1
            self.robot.direct_kinematics()  # We update the euler angles and xyz
            xyz,euler_angles = self.robot.config.cords,self.robot.config.euler_angles
            #Previous state:
            x, y,z = xyz
            A, B,C = euler_angles
            #CONTROLS FOR POSITIONS

            b = self.buttons
            #---y---
            if(b["LeftJoystickX"] !=0):
                y+= sign(b["LeftJoystickX"] )*self.dir_step*dt
            #---x---
            if(b["LeftJoystickY"] !=0):
                x+= sign(b["LeftJoystickY"] )*self.dir_step*dt

            #---Z Down
            if(b["LeftTrigger"] !=0):
                z-= self.dir_step*dt
            
            #---Z up
            if(b["RightTrigger"] !=0):
                z+= self.dir_step*dt
            
            angle_step_positive = Angle(self.angle_step*dt, "rad")
            angle_step_negative = Angle(-self.angle_step*dt, "rad")


            #-- A --

            if(b["LeftBumper"] !=0):
                A.add(angle_step_negative)

            if(b["RightBumper"] !=0):
                A.add(angle_step_positive)

                   
            # -- B --

            if(b["RightJoystickY"] !=0):
                if(sign(b["RightJoystickY"] )>=0):
                    B.add(angle_step_positive)
                else:
                    B.add(angle_step_negative)

             #-- C --

            if(b["RightJoystickX"] !=0):
                if(sign(b["RightJoystickX"] )>=0):
                    C.add(angle_step_positive)
                else:
                    C.add(angle_step_negative)
           

            try:
                self.controller.move_to_point(filemanager.Config([x, y, z], [A, B,C],self.tool))
            except:
                x, y,z = xyz
                A, B,C = euler_angles
            time.sleep(max(0,(1/self.fps)-dt))

if __name__ == '__main__':
    joy = XboxController()
    while True:
        print(joy.read())