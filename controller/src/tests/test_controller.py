import time
import unittest
from typing import Tuple

import numpy as np

from control.controller import ArmController
from utils.prints import disable_console


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
        self, setting_key: str, init_value: float, change_per_iter: bool = True
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
        # homing_direction
        correct, msg = self.get_and_set_joint_settings("homing_direction", -1, False)
        correct, msg = self.get_and_set_joint_settings("homing_direction", 1, False)

        self.assertTrue(correct, msg)
        # speed_rad/s
        correct, msg = self.get_and_set_joint_settings("speed_rad/s", 1.2)

        self.assertTrue(correct, msg)
        # steps_per_rev_motor_axis
        correct, msg = self.get_and_set_joint_settings("steps_per_rev_motor_axis", 220)
        correct, msg = self.get_and_set_joint_settings("steps_per_rev_motor_axis", 5000, False)

        self.assertTrue(correct, msg)
        # conversion_rate_axis_joints
        correct, msg = self.get_and_set_joint_settings("conversion_rate_axis_joints", 1.128)
        correct, msg = self.get_and_set_joint_settings("conversion_rate_axis_joints", 1, False)

        self.assertTrue(correct, msg)
        # homing_offset_rads
        correct, msg = self.get_and_set_joint_settings("homing_offset_rads", np.pi / 7)
        correct, msg = self.get_and_set_joint_settings("homing_offset_rads", np.pi / 4, False)

        self.assertTrue(correct, msg)

    @disable_console
    def test_speed_settings(self) -> None:
        # set speed to 1 rad/s
        self.controller.set_setting_joints("speed_rad/s", 1)
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")

        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        # set speed to 0.5 rad/s
        self.controller.set_setting_joints("speed_rad/s", 0.5)
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time > 1.9, msg=f"Expected 2s, got {end_time - start_time}")
        self.controller.set_setting_joints("speed_rad/s", 1)

    @disable_console
    def test_speed_with_modified_settings(self) -> None:
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        # set conversion rate to 1.5
        self.controller.set_setting_joints("conversion_rate_axis_joints", 1.5)
        self.controller.set_setting_joint("conversion_rate_axis_joints", 4, 2)
        self.controller.set_setting_joint("conversion_rate_axis_joints", 0.5, 1)
        # set steps per
        self.controller.set_setting_joints("steps_per_rev_motor_axis", 1000)
        self.controller.set_setting_joint("steps_per_rev_motor_axis", 3434, 0)
        self.controller.set_setting_joint("steps_per_rev_motor_axis", 6457, 3)

        # move to 1
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")
