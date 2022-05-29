import sys
import os.path

from matplotlib.pyplot import connect


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from inputs import get_gamepad
from inputs import get_key
import keyboard
import math
import threading
import time
from arm_utils import filemanager
from arm_utils.armTransforms import Angle,gen_curve_points
from collections import defaultdict

__author__ = "Alberto Abarzua"


class XboxController(object):
    """XboxController class, used to get inputs from an xbox controller.

    """
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):
        """XboxController, creates buttons dictionary and starts the monitor thread.
        """
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
        self.cooldowns = defaultdict(lambda : 0)
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        

    
    def clean_trigger(self,val):
        """Used to get a clean value from a trigger event

        Args:
            val (float): input form trigger event

        Returns:
            int: cleaned value
        """
        tolerance = 0.1
        pre = val/XboxController.MAX_TRIG_VAL
        if (abs(pre)<tolerance):
            return 0
        return pre
    def clean_joy(self,val):
        """Used to get a clean value from a joystick event

        Args:
            val (float): input form trigger event

        Returns:
            int: cleaned value
        """
        tolerance = 0.3
        pre = val/XboxController.MAX_JOY_VAL
        if (abs(pre)<tolerance):
            return 0
        return pre

 
    def _monitor_controller(self):
        """Gets the events from the gamepad and modifies the buttons dictionary accordingly
        """
        connected = True
        while True:
            try:
                events = get_gamepad()

            except Exception as e:
                print("No GamePad Connected!")
                return
            for event in events:
                print(event.code)
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
                    self.buttons["Y"] = event.state
                elif event.code == 'BTN_WEST':
                    self.buttons["X"] = event.state
                elif event.code == 'BTN_EAST':
                    self.buttons["B"] = event.state
                elif event.code == 'BTN_THUMBL':
                    self.buttons["LeftThumb"] = event.state
                elif event.code == 'BTN_THUMBR':
                    self.buttons["RightThumb"] = event.state
                elif event.code == 'BTN_SELECT':
                    self.buttons["Start"] = event.state
                elif event.code == 'BTN_START':
                    self.buttons["Back"] = event.state
                elif event.code == 'ABS_HAT0X' :
                    if(event.state==-1):
                        self.buttons["LeftDPad"] = abs(event.state)
                    elif(event.state ==1):
                        self.buttons["RightDPad"] = abs(event.state)
                    else:
                        self.buttons["LeftDPad"] = abs(event.state)
                        self.buttons["RightDPad"] = abs(event.state)

                elif event.code == 'ABS_HAT0Y' :
                    if(event.state==-1):
                        self.buttons["UpDPad"] = abs(event.state)
                    elif(event.state ==1):
                        self.buttons["DownDPad"] = abs(event.state)
                    else:
                        self.buttons["UpDPad"] = abs(event.state)
                        self.buttons["DownDPad"] = abs(event.state)




if __name__ == '__main__':
    """ Used to test the inputs of the xbox controller."""
    joy = XboxController()
    while True:
        b ={x:y for x,y in joy.buttons.items() if y!=0}
        print(b) #Print the inputs.
        continue
    