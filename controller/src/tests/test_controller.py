import time
import unittest

from control.controller import ArmController
from utils.prints import disable_console


class TestController(unittest.TestCase):
    @classmethod
    @disable_console
    def setUpClass(cls):
        cls.controller = ArmController()
        cls.controller.start()
        start_time = time.time()
        while not cls.controller.is_ready:
            time.sleep(0.1)
            if time.time() - start_time > 3:
                raise TimeoutError("Controller took too long to start")


    @classmethod
    @disable_console
    def tearDownClass(cls):
        cls.controller.stop()

    @disable_console
    def test_health_check(self):
        self.assertTrue(self.controller.health_check())

    # @disable_console
    # def test_move_to(self):
    #     angles = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    #     self.controller.move_to(angles)
    #     self.assertEqual(self.controller.get_angles(), angles)
