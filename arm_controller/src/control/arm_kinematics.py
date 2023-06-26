import dataclasses

import numpy as np

from utils.algebra import (
    create_rotation_matrix_from_euler_angles,
    degree2rad,
    extract_euler_angles,
    nearest_by_2pi_ref,
    transformation_matrix,
    x_rotation_matrix,
    y_rotation_matrix,
    z_rotation_matrix,
)
from utils.prints import console

"""
    ----------------------------------------
                    Helper Classes
    ----------------------------------------
"""


class Joint:
    def __init__(self, min_val=-2 * np.pi, max_val=2 * np.pi):
        self.min_val = min_val
        self.max_val = max_val

    def in_bounds(self, angle):
        return angle >= self.min_val and angle <= self.max_val

    def set_bounds(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val


class ArmParameters:
    def __init__(self):
        # J1
        self.a1x = 0
        self.a1y = 0
        self.a1z = 0
        # J2
        self.a2x = 0
        self.a2y = 0
        self.a2z = 0
        # J3
        self.a3x = 0
        self.a3y = 0
        self.a3z = 0
        # J4
        self.a4x = 0
        self.a4y = 0
        self.a4z = 0
        # J5
        self.a5x = 0
        self.a5y = 0
        self.a5z = 0
        # J6
        self.a6x = 0
        self.a6z = 0
        self.a6y = 0

        self.joint_ratios = []

        self.j1 = Joint()
        self.j2 = Joint()
        self.j3 = Joint()
        self.j4 = Joint()
        self.j5 = Joint()
        self.j6 = Joint()

        self.joints = [self.j1, self.j2, self.j3, self.j4, self.j5, self.j6]


@dataclasses.dataclass
class ArmPose:
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float

    tool_pos: float = 90

    def __init__(self, x, y, z, roll, pitch, yaw, degree=False):
        self.x = x
        self.y = y
        self.z = z
        if degree:
            self.roll = degree2rad(roll)
            self.pitch = degree2rad(pitch)
            self.yaw = degree2rad(yaw)
        else:
            self.roll = roll
            self.pitch = pitch
            self.yaw = yaw

    @property
    def as_tuple(self):
        return (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)

    @property
    def as_list(self):
        return list(self.as_tuple)


"""
    ----------------------------------------
                    ArmKinematics
    ----------------------------------------
"""


class ArmKinematics:
    def __init__(self, controller):
        self.controller = controller
        self.arm_params = controller.arm_params
        self._test_pose = self.current_pose
        self.test_angles = self.pose_to_angles(self._test_pose)

    @property
    def current_pose(self):
        current_angles = self.controller.current_angles[:]
        return self.angles_to_pose(current_angles)

    def angles_to_pose(self, angles):
        # len of angles must be length of joints
        if len(angles) != len(self.arm_params.joints):
            raise ValueError("angles must be the same length as joints")

        J1, J2, J3, J4, J5, J6 = angles

        R1 = z_rotation_matrix(J1)

        D1 = np.array([self.arm_params.a1x, self.arm_params.a1y, self.arm_params.a1z])
        T1 = transformation_matrix(R1, D1)
        # J1 -->  J2
        R2 = y_rotation_matrix(J2)

        D2 = np.array([self.arm_params.a2x, self.arm_params.a2y, self.arm_params.a2z])
        T2 = transformation_matrix(R2, D2)
        # J2 -->  J3
        R3 = y_rotation_matrix(J3)

        D3 = np.array([self.arm_params.a3x, self.arm_params.a3y, self.arm_params.a3z])
        T3 = transformation_matrix(R3, D3)
        # J3 -->  J4

        R4 = x_rotation_matrix(J4)

        D4 = np.array([self.arm_params.a4x, self.arm_params.a4y, self.arm_params.a4z])
        T4 = transformation_matrix(R4, D4)
        # J4 -->  J5
        R5 = y_rotation_matrix(J5)

        D5 = np.array([self.arm_params.a5x, self.arm_params.a5y, self.arm_params.a5z])
        T5 = transformation_matrix(R5, D5)
        # J5 -->  J6
        R6 = x_rotation_matrix(J6)
        D6 = np.array([self.arm_params.a6x, self.arm_params.a6y, self.arm_params.a6z])

        T6 = transformation_matrix(R6, D6)
        # Base--> TCP
        position = T1 @ T2 @ T3 @ T4 @ T5 @ T6 @ np.array([[0], [0], [0], [1]])
        rotation = R1 @ R2 @ R3 @ R4 @ R5 @ R6
        euler_angles = extract_euler_angles(rotation)
        pos = list(position[:3, 0])

        return ArmPose(*pos, *euler_angles)

    def pose_to_angles(self, target_pose):
        try:
            current_angles = self.controller.current_angles
            found_angles = self._pose_to_angles(target_pose, current_angles)
            return found_angles
        except Exception as e:
            console.print(f"Error in pose_to_angles: {e}", style="error")
            return None

    def _pose_to_angles(self, target_pose, current_angles=None):
        if current_angles is None:
            current_angles = [0 for _ in range(len(self.arm_params.joints))]

        prev_angles = current_angles
        J1_prev = prev_angles[0]
        J4_prev = prev_angles[3]

        x, y, z, roll, pitch, yaw = target_pose.as_tuple

        TCP = np.array([[x], [y], [z]])
        xdirection = create_rotation_matrix_from_euler_angles(roll, pitch, yaw) @ np.array(
            [[1], [0], [0]]
        )

        WP = TCP - self.arm_params.a6x * xdirection
        # Finding J1,J2,J3

        J1 = np.arctan2(WP[1, 0], WP[0, 0])

        if WP[0, 0] == 0 and WP[1, 0] == 0:
            J1 = J1_prev
        WPxy = np.sqrt(WP[0, 0] ** 2 + WP[1, 0] ** 2)
        L = WPxy - self.arm_params.a2x
        H = WP[2, 0] - self.arm_params.a1z - self.arm_params.a2z
        P = np.sqrt(H**2 + L**2)
        b4x = np.sqrt(
            self.arm_params.a4z**2 + (self.arm_params.a4x + self.arm_params.a5x) ** 2
        )
        if (P <= self.arm_params.a3z + b4x) and abs(self.arm_params.a3z - b4x) < P:
            alfa = np.arctan2(H, L)
            cosbeta = (P**2 + self.arm_params.a3z**2 - b4x**2) / (
                2 * P * self.arm_params.a3z
            )
            beta = np.arctan2(np.sqrt(1 - cosbeta**2), cosbeta)
            cosgamma = (self.arm_params.a3z**2 + b4x**2 - P**2) / (
                2 * self.arm_params.a3z * b4x
            )
            gamma = np.arctan2(np.sqrt(1 - cosgamma**2), cosgamma)
            delta = np.arctan2(self.arm_params.a4x + self.arm_params.a5x, self.arm_params.a4z)
            J2 = np.pi / 2.0 - alfa - beta
            J3 = np.pi - gamma - delta
            # Finding Wrist Orientation
            R1 = z_rotation_matrix(J1)
            R2 = y_rotation_matrix(J2)
            R3 = y_rotation_matrix(J3)
            Rarm = R1 @ R2 @ R3
            Rarmt = Rarm.transpose()
            R = create_rotation_matrix_from_euler_angles(roll, pitch, yaw)
            Rwrist = Rarmt @ R
            # Finding J4
            J5 = np.arctan2(np.sqrt(1 - Rwrist[0, 0] ** 2), Rwrist[0, 0])
            if J5 == 0:  # Singularity
                J4 = J4_prev  # keep the current angle of J4.
                J6 = np.arctan2(Rwrist[2, 1], Rwrist[2, 2]) - J4
            else:
                J4_1 = np.arctan2(Rwrist[1, 0], -Rwrist[2, 0])
                J4_2 = -np.arctan2(Rwrist[1, 0], Rwrist[2, 0])

                J6_1 = np.arctan2(Rwrist[0, 1], Rwrist[0, 2])
                J6_2 = -np.arctan2(Rwrist[0, 1], -Rwrist[0, 2])
                if abs(J4_prev - J4_1) > abs(J4_prev - J4_2):
                    J4 = J4_2
                    J6 = J6_2
                    J5 = np.arctan2(-np.sqrt(1 - Rwrist[0, 0] ** 2), Rwrist[0, 0])
                else:
                    J4 = J4_1
                    J6 = J6_1
            found_angles = [J1, J2, J3, J4, J5, J6]
            return [
                nearest_by_2pi_ref(angle, ref) for angle, ref in zip(found_angles, prev_angles)
            ]
