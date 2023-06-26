import unittest

import numpy as np

from control.arm_kinematics import ArmPose
from control.controller import ArmController
from utils.algebra import (
    create_rotation_matrix_from_euler_angles,
    degree2rad,
    extract_euler_angles,
)
from utils.prints import disable_console


class TestArmKinematics(unittest.TestCase):
    EPSILON = 0.01

    def helper_angle_to_pose(self, angles, expected_pose):
        angles = [degree2rad(angle) for angle in angles]
        current_pose = self.controller.kinematics.angles_to_pose(angles)
        current_pose = current_pose.as_list
        expected_pose = expected_pose.as_list
        all_close = np.allclose(current_pose, expected_pose, rtol=self.EPSILON)
        self.assertTrue(all_close, f"expected: {expected_pose} actual: {current_pose}")

    def helper_pose_to_angles(self, expected_angles, pose):
        """Helper method used to test inverse_kinematics (IK) from a configuration of
          positions and euler angles.

        Args:
            joints (list[Angle]): Expected angles for the robot (what IK should return)
            pos (list[float]): x,y,z positions of config
            euler (list[Angle]): A,B,C euler angles of config
        """
        angles = self.controller.kinematics.pose_to_angles(pose)
        expected_angles = [degree2rad(angle) for angle in expected_angles]
        all_close = np.allclose(angles, expected_angles, rtol=self.EPSILON)
        self.assertTrue(all_close, f"expected: {expected_angles} actual: {angles}")

    @classmethod
    @disable_console
    def setUpClass(cls):
        cls.controller = ArmController()
        cls.controller.arm_params.a1z = 650
        cls.controller.arm_params.a2x = 400
        cls.controller.arm_params.a2z = 680
        cls.controller.arm_params.a3z = 1100
        cls.controller.arm_params.a4z = 230
        cls.controller.arm_params.a4x = 766
        cls.controller.arm_params.a5x = 345
        cls.controller.arm_params.a6x = 244

    @disable_console
    def test_pose_to_angles(self):
        pose = ArmPose(1755, 0, 2660, 0, 0, 0, degree=True)
        self.helper_pose_to_angles([0, 0, 0, 0, 0, 0], pose)

        pose = ArmPose(0, 1755, 2660, 0, 0, 90, degree=True)
        self.helper_pose_to_angles([90, 0, 0, 0, 0, 0], pose)

        pose = ArmPose(1500, 1000, 2000, 0, 0, 0, degree=True)
        self.helper_pose_to_angles([38.5, 7.9, 25.5, 55.3, -49.2, -43.3], pose)

        pose = ArmPose(-500, 1000, 2000, 50, 50, 50, degree=True)
        self.helper_pose_to_angles([124.3, -24.7, 43.6, -42.8, 65.6, 140.8], pose)

        pose = ArmPose(600, -1000, 3300, 250, 0, -90, degree=True)
        self.helper_pose_to_angles([-51.6, -7.9, -31.3, -51.5, 52.6, -72.7], pose)

    @disable_console
    def test_angles_to_pose(self):
        self.helper_angle_to_pose(
            [0, 0, 0, 0, 0, 0], ArmPose(1755, 0, 2660, 0, 0, 0, degree=True)
        )

        self.helper_angle_to_pose(
            [90, 0, 0, 0, 0, 0], ArmPose(0, 1755, 2660, 0, 0, 90, degree=True)
        )

        self.helper_angle_to_pose(
            [130, -60, 30, 60, -90, 60],
            ArmPose(11.8, 314.7, 2740.3, -176.3, -25.7, 23.9, degree=True),
        )

        self.helper_angle_to_pose(
            [-46, 46, 46, 46, 46, 46],
            ArmPose(962.3, -814.8, 810.6, -132.0, 42.6, 89.3, degree=True),
        )

    @disable_console
    def test_angle_to_pose_to_angle(self):
        angles = [np.pi / 2 for _ in range(6)]
        pose = self.controller.kinematics.angles_to_pose(angles)
        angles2 = self.controller.kinematics.pose_to_angles(pose)
        all_close = np.allclose(angles, angles2, rtol=self.EPSILON)
        self.assertTrue(all_close, f"expected: {angles} actual: {angles2}")

    @disable_console
    def test_rotation_matrixs(self):
        R1 = create_rotation_matrix_from_euler_angles(90, 100, 20)

        roll, pitch, yaw = extract_euler_angles(R1)
        R2 = create_rotation_matrix_from_euler_angles(roll, pitch, yaw)
        all_close = np.allclose(R1, R2, rtol=self.EPSILON)
        self.assertTrue(all_close, f"expected: {R1} actual: {R2}")
