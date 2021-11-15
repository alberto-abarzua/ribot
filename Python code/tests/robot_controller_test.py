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

    def angleAllClose(self,L1,L2):
        """Helper method used to check if two Angle list have almost the same values.

        Args:
            L1 (list[Angle]): first list
            L2 (list[Angle]): second list
        Returns:
            bool: if all the angles are close.
        """
        L1=  [angle.rad for angle in L1]
        L2 = [angle.rad for angle in L2]
        return np.allclose(L1,L2,atol=1/self.controller.acc)
    def setUp(self):
        self.controller = ctrl.Controller()
        self.arduino = self.controller.arduino

    def test_initial_arduino_state(self):
        self.assertEqual("1\n",self.controller.read())
    
    def test_move_command(self):
        joints = [Angle(np.pi,"rad"),Angle(2*np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad"),Angle(np.pi,"rad")]
        self.controller.move_command(joints)
        self.assertEquals("m7 31416 62832 62832 31416 31416 31416 31416",self.arduino.received_lines[0])
        self.assertEqual([31416,62832, 31416, 31416, 31416 ,31416],self.controller.arduino_angles)
        self.assertTrue(self.angleAllClose(joints,self.controller.get_arduino_angles()))
        self.controller.move_command(joints)
        self.assertEquals("m7 31416 62832 62832 31416 31416 31416 31416",self.arduino.received_lines[1])
        self.assertEqual([62832,125664, 62832, 62832, 62832 ,62832],self.controller.arduino_angles)
        joints = [Angle(angle.rad*2,"rad") for angle in joints]
        self.assertTrue(self.angleAllClose(joints,self.controller.get_arduino_angles()))

    def test_move_to_point(self):
        cords = [326,0,334]
        euler = [Angle(0,"rad"),Angle(0,"rad"),Angle(0,"rad")]
        self.controller.move_to_point(cords = cords,angles = euler) ##Moving to initial position
        self.assertTrue("m7 0 0 0 0 0 0 0",self.arduino.received_lines[0])
        self.assertTrue(self.angleAllClose([Angle(0,"rad") for _ in range(6)],self.controller.get_arduino_angles()))
        
        joints = [Angle(np.pi/8,"rad"),Angle(2*np.pi/8,"rad"),Angle(np.pi/8,"rad"),Angle(np.pi/8,"rad"),Angle(np.pi/8,"rad"),Angle(np.pi/8,"rad")]
        cords,euler = self.controller.robot.direct_kinematics(joints)

        self.controller.move_to_point(cords = cords,angles = euler) ##Moving to initial position
        self.assertEquals("m7 3927 7854 7854 3927 3927 3927 3927",self.arduino.received_lines[1])
        self.assertTrue(self.angleAllClose(joints,self.controller.get_arduino_angles()))

        



if __name__ == '__main__':
    unittest.main()