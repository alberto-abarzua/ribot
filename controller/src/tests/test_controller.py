import time
import unittest

import numpy as np

from control.controller import ArmController
from utils.prints import disable_console


class TestController(unittest.TestCase):
    @classmethod
    @disable_console
    def setUpClass(cls):
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
    def tearDownClass(cls):
        cls.controller.stop()

    @disable_console
    def tearDown(self) -> None:
        self.controller.move_to_angles([0, 0, 0, 0, 0, 0])
        self.controller.wait_queue_empty()

    @disable_console
    def test_health_check(self):
        self.assertTrue(self.controller.health_check())

    @disable_console
    def test_move_to(self):
        angles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        epsilon = 0.01
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(
            all_close, msg=f"Expected {angles}, got {self.controller.current_angles}"
        )
        angles = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)
        self.assertTrue(
            all_close, msg=f"Expected {angles}, got {self.controller.current_angles}"
        )
        angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.controller.move_to_angles(angles)
        self.controller.wait_queue_empty()
        all_close = np.allclose(self.controller.current_angles, angles, atol=epsilon)

    @disable_console
    def test_double_home(self):
        self.controller.home()
        self.assertTrue(
            np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1)
        )
        self.assertTrue(self.controller.is_homed)
        self.controller.home()
        self.assertTrue(self.controller.is_homed)
        self.assertTrue(
            np.allclose(self.controller.current_angles, [0, 0, 0, 0, 0, 0], atol=0.1)
        )
