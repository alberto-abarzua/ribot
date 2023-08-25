import time
import unittest
from typing import Tuple

import numpy as np

from robot_arm_controller.controller import ArmController, Settings
from robot_arm_controller.utils.prints import disable_console


class TestController(unittest.TestCase):
    controller: ArmController
    EPSILON = 0.01

    @classmethod
    @disable_console
    def setUpClass(cls) -> None:
        cls.controller = ArmController()
        cls.controller.start(websocket_server=False)
        start_time = time.time()
        while not cls.controller.is_ready:
            time.sleep(0.1)
            if time.time() - start_time > 3:
                # fail all tests if controller takes too long to start
                raise TimeoutError("Controller took too long to start")

        cls.controller.home()

    @classmethod
    @disable_console
    def tearDownClass(cls) -> None:
        cls.controller.stop()

    @disable_console
    def tearDown(self) -> None:
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.wait_done_moving()

    @disable_console
    def test_health_check(self) -> None:
        self.assertTrue(self.controller.health_check())

    @disable_console
    def test_move_to(self) -> None:
        angles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()
        epsilon = 0.01
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")
        angles = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")
        angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        # test negative numbers
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")
        angles = [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")

    @disable_console
    def test_double_home(self) -> None:
        self.controller.home()
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))
        self.assertTrue(self.controller.is_homed)
        self.controller.home()
        self.assertTrue(self.controller.is_homed)
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))

    def get_and_set_joint_settings(
        self, setting_key: Settings, init_value: float, change_per_iter: bool = True
    ) -> Tuple[bool, str]:
        # homing_direction
        correct = True
        for i in range(self.controller.num_joints):
            if change_per_iter:
                value = init_value + i
            else:
                value = init_value
            self.controller.set_setting_joint(setting_key, value, i)
            setting = self.controller.get_setting_joint(setting_key, i)
            correct = correct and (abs(setting - value) < self.EPSILON)
        return correct, f"Expected {value}, got {setting}"

    @disable_console
    def test_joint_settings(self) -> None:
        correct, msg = self.get_and_set_joint_settings(Settings.HOMING_DIRECTION, -1, False)
        correct, msg = self.get_and_set_joint_settings(Settings.HOMING_DIRECTION, 1, False)

        self.assertTrue(correct, msg)
        correct, msg = self.get_and_set_joint_settings(Settings.SPEED_RAD_PER_S, 1.2)

        self.assertTrue(correct, msg)
        correct, msg = self.get_and_set_joint_settings(Settings.STEPS_PER_REV_MOTOR_AXIS, 220)
        correct, msg = self.get_and_set_joint_settings(Settings.STEPS_PER_REV_MOTOR_AXIS, 5000, False)

        self.assertTrue(correct, msg)
        correct, msg = self.get_and_set_joint_settings(Settings.CONVERSION_RATE_AXIS_JOINTS, 1.128)
        correct, msg = self.get_and_set_joint_settings(Settings.CONVERSION_RATE_AXIS_JOINTS, 1, False)

        self.assertTrue(correct, msg)
        correct, msg = self.get_and_set_joint_settings(Settings.HOMING_OFFSET_RADS, np.pi / 7)
        correct, msg = self.get_and_set_joint_settings(Settings.HOMING_OFFSET_RADS, np.pi / 4, False)

        self.assertTrue(correct, msg)

    @disable_console
    def test_speed_settings(self) -> None:
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 1)
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")

        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.5)
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time > 1.9, msg=f"Expected 2s, got {end_time - start_time}")
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 1)

    @disable_console
    def test_speed_with_modified_settings(self) -> None:
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.set_setting_joints(Settings.CONVERSION_RATE_AXIS_JOINTS, 1.5)
        self.controller.set_setting_joint(Settings.CONVERSION_RATE_AXIS_JOINTS, 4, 2)
        self.controller.set_setting_joint(Settings.CONVERSION_RATE_AXIS_JOINTS, 0.5, 1)
        self.controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 1000)
        self.controller.set_setting_joint(Settings.STEPS_PER_REV_MOTOR_AXIS, 3434, 0)
        self.controller.set_setting_joint(Settings.STEPS_PER_REV_MOTOR_AXIS, 6457, 3)

        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")
