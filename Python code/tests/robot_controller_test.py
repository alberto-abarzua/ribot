import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import arm_utils.robotarm as robotarm
from arm_utils.armTransforms import Angle
import arm_utils.armTransforms as util
import arm_control.controller as ctrl
import unittest

__author__ = "Alberto Abarzua"

class robot_controller_tests(unittest.TestCase):

    def setUp(self):
        self.controller = ctrl.Controller()
        self.arduino = self.controller.arduino

    def test_initial_arduino_state(self):
        self.assertEqual("1\n",self.controller.read())
    


    def test_move_command(self):
        joints = [Angle(np.pi,"rad"),Angle(2*np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad")]
        self.controller.move_command(joints)
        self.assertEquals("m7 31415 62831 62831 31415 31415 31415 31415",self.arduino.received_lines[0])



if __name__ == '__main__':
    unittest.main()