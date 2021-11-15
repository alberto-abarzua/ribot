import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from arm_utils.armTransforms import Angle
import arm_utils.armTransforms as util
import unittest

__author__ = "Alberto Abarzua"

class testarm_utils(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_angle(self):
        angle1 = Angle(90, "deg")
        self.assertEqual(np.pi/2, angle1.rad)
        self.assertEqual(90, angle1.deg)
        angle2 = Angle(np.pi/2, "rad")
        self.assertEqual(90, angle2.deg)
        self.assertEqual(np.pi/2, angle2.rad)

    def test_angle_equals(self):
        a1 = Angle(90, "deg")
        a2 = Angle(90, "deg")
        a3 = Angle(np.pi/2, "rad")
        self.assertEqual(a1, a2)
        self.assertEqual(a1.deg, a2.deg)
        self.assertEqual(a1.rad, a2.rad)
        self.assertEqual(a1, a3)

    def test_euler_angle(self):
        R1 = util.zmatrix(Angle(20, "deg"))@util.ymatrix(Angle(100,
                                                               "deg"))@util.xmatrix(Angle(90, "deg"))
        A, B, C = util.rotationMatrixToEulerAngles(R1)
        R2 = util.eulerAnglesToRotMatrix(A, B, C)
        self.assertTrue(np.allclose(R1, R2))
    def test_nearest_to_prev(self):
        prev = [Angle(10,"deg"),Angle(100,"deg"),Angle(270,"deg")]
        angle = [Angle(270,"deg"),Angle(170,"deg"),Angle(-90,"deg")]
        self.assertEqual([Angle(-90,"deg"),Angle(170,"deg"),Angle(270,"deg")],util.nearest_to_prev(angle,prev))

