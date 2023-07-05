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
        self.controller.wait_queue_empty()

    @disable_console
    def test_health_check(self) -> None:
        self.assertTrue(self.controller.health_check())

    @disable_console
    def test_move_to(self) -> None:
        angles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        epsilon = 0.01
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")
        angles = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")
        angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)

    @disable_console
    def test_double_home(self) -> None:
        self.controller.home()
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))
        self.assertTrue(self.controller.is_homed)
        self.controller.home()
        self.assertTrue(self.controller.is_homed)
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))

    def get_and_set_joint_settings(self, setting_key: str, value: float) -> Tuple[bool, str]:
        # homing_direction
        correct = True
        for i in range(self.controller.num_joints):
            self.controller.set_setting_joint(setting_key, i, value)
            setting = self.controller.get_setting_joint(setting_key, i)
            correct = correct and (abs(setting - value) < self.EPSILON)
        return correct, f"Expected {value}, got {setting}"

    @disable_console
    def test_joint_settings(self) -> None:
        # homing_direction
        correct, msg = self.get_and_set_joint_settings("homing_direction", -1)
        self.assertTrue(correct, msg)
        # speed_rad/s
        correct, msg = self.get_and_set_joint_settings("speed_rad/s", 1.2)
        self.assertTrue(correct, msg)
        # steps_per_rev_motor_axis
        correct, msg = self.get_and_set_joint_settings("steps_per_rev_motor_axis", 220)
        self.assertTrue(correct, msg)
        # conversion_rate_axis_joints
        correct, msg = self.get_and_set_joint_settings("conversion_rate_axis_joints", 1.128)
        self.assertTrue(correct, msg)
        # homing_offset_rads
        correct, msg = self.get_and_set_joint_settings("homing_offset_rads", np.pi / 7)
        self.assertTrue(correct, msg)
