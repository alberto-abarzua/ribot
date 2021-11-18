import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import arm_control.filemanager as filem
import arm_control.commands as com
import unittest
import arm_control.controller as ctrl
import arm_utils.armTransforms as util
from arm_utils.armTransforms import Angle
import arm_utils.robotarm as robotarm
import numpy as np

__author__ = "Alberto Abarzua"


class file_manager_test(unittest.TestCase):

    def angleAllClose(self, L1, L2):
        """Helper method used to check if two Angle list have almost the same values.

        Args:
            L1 (list[Angle]): first list
            L2 (list[Angle]): second list
        Returns:
            bool: if all the angles are close.
        """
        L1 = [angle.rad for angle in L1]
        L2 = [angle.rad for angle in L2]
        return np.allclose(L1, L2, atol=1/1000)

    def test_instructions(self):
        p1 = ([300, 0, 300], [Angle(0, "rad"), Angle(0, "rad"), Angle(0, "rad")])
        p2 = ([320, 0, 320], [Angle(0, "rad"), Angle(90, "deg"), Angle(0, "rad")])
        p1_instruction = filem.CordAngleInstruction(p1)
        p2_instruction = filem.CordAngleInstruction(p2)
        self.assertEqual("c 300 0 300 0 0 0\n", p1_instruction.line)
        self.assertEqual("c 320 0 320 0 1.57079633 0\n", p2_instruction.line)
        p2_fromstring = filem.CordAngleInstruction(
            "c 320 0 320 0 1.57079633 0\n")
        self.assertEqual("c 320 0 320 0 1.57079633 0\n", p2_fromstring.line)
        self.assertEqual(p2[0], p2_fromstring.as_tuple()[0])
        self.assertTrue(self.angleAllClose(p2[1], p2_fromstring.as_tuple()[1]))

    def test_run(self):
        controller = ctrl.Controller()
        controller.arduino.set_log_file("test1_arduino.txt")
        p1 = ([326.55, 1, 334], [Angle(0, "deg"),
              Angle(0, "deg"), Angle(0, "deg")])
        p2 = ([367, 1, 334], [Angle(10, "deg"), Angle(0, "deg"), Angle(0, "deg")])
        curve = controller.generate_curve_ptp(p1=p1, p2=p2, n=500)

        f = filem.FileManager()
        instructions = f.from_curve_to_instruct(curve)
        f.write_file(instructions, "test1.txt")

        controller.run_file("arm_control/data/test1.txt")
        while(controller.step()):
            continue
        controller.arduino.log.close()
        f1 = open("tests/test_data/expected_test1_arduino.txt", "r")
        f2 = open("tests/test_data/test1_arduino.txt", "r")
        self.assertEqual(f1.readlines(), f2.readlines())
        f1.close()
        f2.close()


if __name__ == '__main__':
    unittest.main()
