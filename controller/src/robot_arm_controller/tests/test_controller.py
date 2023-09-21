import os
import time
import unittest
from typing import Tuple

import numpy as np

from robot_arm_controller.control.arm_kinematics import ArmParameters
from robot_arm_controller.controller import ArmController, Settings
from robot_arm_controller.utils.prints import console


class TestController(unittest.TestCase):
    controller: ArmController
    EPSILON = 0.1

    @classmethod
    def setUpClass(cls) -> None:
        console.log("Starting test_controller.py!", style="bold green")

        # Arm parameters
        arm_params: ArmParameters = ArmParameters()
        arm_params.a2x = 0
        arm_params.a2z = 172.48

        arm_params.a3z = 173.5

        arm_params.a4z = 0
        arm_params.a4x = 126.2

        arm_params.a5x = 64.1
        arm_params.a6x = 169

        cls.controller = ArmController(arm_parameters=arm_params)
        cls.controller.start(websocket_server=False, wait=True)

        cls.controller.print_status = os.environ.get("PRINT_STATUS", "False").upper() == "TRUE"
        console.log("Runing with print_status:", cls.controller.print_status, style="bold green")

        cls.controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 800)
        cls.controller.set_setting_joints(Settings.CONVERSION_RATE_AXIS_JOINTS, 1)
        cls.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.3)
        cls.controller.set_setting_joints(Settings.HOMING_OFFSET_RADS, np.pi / 4)
        cls.controller.home()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.controller.stop()

    def tearDown(self) -> None:
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.wait_done_moving()

    def test_health_check(self) -> None:
        console.log("Running test: test_health_check", style="bold yellow")
        self.assertTrue(self.controller.health_check())

    def test_move_to(self) -> None:
        console.log("Running test: test_move_to", style="bold yellow")
        epsilon = 0.01

        self.controller.wait_done_moving()

        angles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()

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
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")

        angles = [-0.1, -0.2, -0.3, -0.4, -0.5, -0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_done_moving()

        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(all_close, msg=f"Expected {angles}, got {self.controller.current_angles}")

    def test_double_home(self) -> None:
        console.log("Running test: test_double_home", style="bold yellow")
        self.controller.wait_done_moving()
        self.controller.home()
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))
        self.assertTrue(self.controller.is_homed)
        self.controller.home()
        self.assertTrue(self.controller.is_homed)
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))

    def get_and_set_joint_settings(
        self, setting_key: Settings, init_value: float, change_per_iter: bool = True
    ) -> Tuple[bool, str]:
        console.log(f"Running test: test_joint_settings for {setting_key}", style="bold yellow")

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

    def test_joint_settings(self) -> None:
        console.log("Running test: test_joint_settings", style="bold yellow")
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

    def test_speed_settings(self) -> None:
        console.log("Running test: test_speed_settings", style="bold yellow")
        self.controller.wait_done_moving()
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 1)
        speeds = self.controller.get_setting_joints(Settings.SPEED_RAD_PER_S)
        self.assertTrue(np.allclose(speeds, [1, 1, 1, 1, 1, 1], atol=0.1))
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.wait_done_moving()
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        speeds = self.controller.get_setting_joints(Settings.SPEED_RAD_PER_S)
        self.assertTrue(np.allclose(speeds, [1, 1, 1, 1, 1, 1], atol=0.1))
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")

        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.5)
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        end_time = time.time()
        self.assertTrue(end_time - start_time > 1.9, msg=f"Expected 2s, got {end_time - start_time}")
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 1)

    def test_set_tool_value(self) -> None:
        console.log("Running test: test_set_tool_value", style="bold yellow")
        self.controller.set_tool_value(0)
        self.controller.wait_done_moving()

        all_close = np.allclose(self.controller.tool_value, 0, atol=0.15)
        self.assertTrue(all_close, msg=f"Expected {0} got {self.controller.tool_value}")

        self.controller.set_tool_value(1)
        self.controller.wait_done_moving()

        all_close = np.allclose(self.controller.tool_value, 1, atol=0.15)
        self.assertTrue(all_close, msg=f"Expected {1} got {self.controller.tool_value}")

        self.controller.set_tool_value(-1)
        self.controller.wait_done_moving()

        all_close = np.allclose(self.controller.tool_value, -1, atol=0.15)
        self.assertTrue(all_close, msg=f"Expected {-1} got {self.controller.tool_value}")

        self.controller.set_tool_value(0.5)
        self.controller.wait_done_moving()

        all_close = np.allclose(self.controller.tool_value, 0.5, atol=0.15)
        self.assertTrue(all_close, msg=f"Expected {0.5} got {self.controller.tool_value}")

        self.controller.set_tool_value(-0.5)
        self.controller.wait_done_moving()
        all_close = np.allclose(self.controller.tool_value, -0.5, atol=0.15)
        self.assertTrue(all_close, msg=f"Expected {-0.5} got {self.controller.tool_value}")

    def test_speed_with_modified_settings(self) -> None:
        console.log("Running test: test_speed_with_modified_settings", style="bold yellow")
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.wait_done_moving()

        self.controller.set_setting_joints(Settings.CONVERSION_RATE_AXIS_JOINTS, 1.5)

        self.controller.set_setting_joint(Settings.CONVERSION_RATE_AXIS_JOINTS, 4, 2)
        self.controller.set_setting_joint(Settings.CONVERSION_RATE_AXIS_JOINTS, 1, 1)
        self.controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 8000)
        self.controller.set_setting_joint(Settings.STEPS_PER_REV_MOTOR_AXIS, 3434, 0)
        self.controller.set_setting_joint(Settings.STEPS_PER_REV_MOTOR_AXIS, 6457, 3)

        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 1)
        speeds = self.controller.get_setting_joints(Settings.SPEED_RAD_PER_S)
        self.assertTrue(np.allclose(speeds, [1, 1, 1, 1, 1, 1], atol=0.1))

        self.controller.wait_done_moving()

        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))
        start_time = time.time()
        self.controller.move_to_angles([1, 1, 1, 1, 1, 1])
        self.controller.wait_done_moving()
        self.assertTrue(np.allclose(self.controller.current_angles, [1, 1, 1, 1, 1, 1], atol=0.1))
        end_time = time.time()
        self.assertTrue(end_time - start_time < 1.4, msg=f"Expected 1s, got {end_time - start_time}")

        speeds = self.controller.get_setting_joints(Settings.SPEED_RAD_PER_S)
        self.assertTrue(np.allclose(speeds, [1, 1, 1, 1, 1, 1], atol=0.1))

    def test_move_queue_size(self) -> None:
        self.controller.wait_done_moving()
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        time.sleep(1)
        self.controller.wait_done_moving()
        self.assertTrue(np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1))
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.4)
        self.controller.move_to_angles([-1, -1, -1, -1, -1, -1])
        time.sleep(1)
        self.assertEqual(self.controller.move_queue_size, 1)
        self.controller.move_to_angles([0.7, 0.7, 0.7, 0.7, 0.7, 0.7])
        self.controller.move_to_angles([0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
        self.controller.move_to_angles([0.9, 0.9, 0.9, 0.9, 0.9, 0.9])
        self.controller.set_tool_value(1)
        time.sleep(1)
        self.assertEqual(self.controller.move_queue_size, 5)
        self.controller.wait_done_moving()
        self.assertEqual(self.controller.move_queue_size, 0)
        self.controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.1)
        self.controller.move_to_angles([-0.7, -0.7, -0.7, -0.7, -0.7, -0.7])
        self.controller.move_to_angles([-0.8, -0.8, -0.8, -0.8, -0.8, -0.8])
        self.controller.move_to_angles([-0.9, -0.9, -0.9, -0.9, -0.9, -0.9])
        # make sure the queue is size 3
        time.sleep(0.5)
        self.assertEqual(self.controller.move_queue_size, 3)
        self.controller.stop_movement()
        time.sleep(0.5)
        self.assertEqual(self.controller.move_queue_size, 0)
