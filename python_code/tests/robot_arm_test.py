import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import arm_utils.armTransforms as util
from arm_utils.armTransforms import Angle, Config
import arm_utils.robotarm as robotarm
import numpy as np

__author__ = "Alberto Abarzua"


class robot_arm_tests(unittest.TestCase):

    def helper_direct_kinematics(self, joints, pos, euler):
        """Helper method used to test direct_kinematics

        Args:
            joints (list[Angle]): angles for the robot joints in deg.
            pos (list[float]): x,y,z expected positions
            euler (list[float]): A,B,C expected euler angles in deg.
        """
        angles = util.angle_list(joints, "deg")
        config = self.robot.direct_kinematics(angles)
        pos_pred, euler_angles_pred = config.cords,config.euler_angles
        self.assertTrue(np.allclose(pos_pred, pos, rtol=1e-01))
        euler_angles_pred = [angle.deg for angle in euler_angles_pred]
        self.assertTrue(np.allclose(euler, euler_angles_pred, rtol=1e-01))

    def helper_inverse_kinematics(self, joints, pos, euler):
        """Helper method used to test inverse_kinematics (IK) from a configuration of positions and euler angles.

        Args:
            joints (list[Angle]): Expected angles for the robot (what IK should return)
            pos (list[float]): x,y,z positions of config
            euler (list[Angle]): A,B,C euler angles of config
        """
        euler = util.angle_list(euler, "deg")
        angles = self.robot.inverse_kinematics(Config(pos, euler))
        angles = [angle.deg for angle in angles]
        self.assertTrue(np.allclose(angles, joints, rtol=1e-01),f"expected: {joints} actual: {angles}")

    def setUp(self):
        # Physical constraints of the robot (measurements in mm)
        self.robot = robotarm.RobotArm()
        self.robot.a1z = 650
        self.robot.a2x = 400
        self.robot.a2z = 680
        self.robot.a3z = 1100
        self.robot.a4z = 230
        self.robot.a4x = 766
        self.robot.a5x = 345
        self.robot.a6x = 244

        return super().setUp()

    def test_direct_kinematics(self):
        self.helper_direct_kinematics(
            [0, 0, 0, 0, 0, 0], [1755, 0, 2660], [0, 0, 0])
        self.helper_direct_kinematics(
            [90, 0, 0, 0, 0, 0], [0, 1755, 2660], [0, 0, 90])
        self.helper_direct_kinematics(
            [130, -60, 30, 60, -90, 60], [11.8, 314.7, 2740.3], [-176.3, -25.7, 23.9])
        self.helper_direct_kinematics(
            [-46, 46, 46, 46, 46, 46], [962.3, -814.8, 810.6], [-132.0, 42.6, 89.3])

    def test_inverse_kinematics(self):
        self.helper_inverse_kinematics(
            [0, 0, 0, 0, 0, 0], [1755, 0, 2660], [0, 0, 0])
        self.helper_inverse_kinematics(
            [90, 0, 0, 0, 0, 0], [0, 1755, 2660], [0, 0, 90])
        self.helper_inverse_kinematics(
            [38.5, 7.9, 25.5, 55.3, -49.2, -43.3], [1500, 1000, 2000], [0, 0, 0])
        self.helper_inverse_kinematics(
            [124.3, -24.7, 43.6, -42.8, 65.6, 140.8], [-500, 1000, 2000], [50, 50, 50])
        self.helper_inverse_kinematics(
            [-51.6, -7.9, -31.3, -51.5, 52.6, -72.7], [600, -1000, 3300], [250, 0, -90])


if __name__ == '__main__':
    unittest.main()
