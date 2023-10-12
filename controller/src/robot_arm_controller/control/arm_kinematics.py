from __future__ import annotations

import dataclasses
from typing import Dict, List, Optional, Tuple

import numpy as np

from robot_arm_controller.utils.algebra import (
    create_rotation_matrix_from_euler_angles,
    degree2rad,
    extract_euler_angles,
    nearest_by_2pi_ref,
    transformation_matrix,
    x_rotation_matrix,
    y_rotation_matrix,
    z_rotation_matrix,
)
from robot_arm_controller.utils.prints import console

"""
    ----------------------------------------
                    Helper Classes
    ----------------------------------------
"""


class Joint:
    def __init__(self, min_val: float = -np.pi / 2, max_val: float = np.pi / 2) -> None:
        self.min_val = min_val
        self.max_val = max_val

    def in_bounds(self, angle: float) -> bool:
        return angle >= self.min_val and angle <= self.max_val

    def set_bounds(self, min_val: float, max_val: float) -> None:
        self.min_val = min_val
        self.max_val = max_val


class ArmParameters:
    def __init__(self) -> None:
        # J1
        self.a1x: float = 0
        self.a1y: float = 0
        self.a1z: float = 0
        # J2
        self.a2x: float = 0
        self.a2y: float = 0
        self.a2z: float = 0
        # J3
        self.a3x: float = 0
        self.a3y: float = 0
        self.a3z: float = 0
        # J4
        self.a4x: float = 0
        self.a4y: float = 0
        self.a4z: float = 0
        # J5
        self.a5x: float = 0
        self.a5y: float = 0
        self.a5z: float = 0
        # J6
        self.a6x: float = 0
        self.a6z: float = 0
        self.a6y: float = 0

        self.joint_ratios: List[float] = []

        self.j1: Joint = Joint()
        self.j2: Joint = Joint()
        self.j3: Joint = Joint()
        self.j4: Joint = Joint()
        self.j5: Joint = Joint()
        self.j6: Joint = Joint()

        self.joints: List[Joint] = [self.j1, self.j2, self.j3, self.j4, self.j5, self.j6]

    def __str__(self) -> str:
        return f"""
        a1x: {self.a1x}
        a1y: {self.a1y}
        a1z: {self.a1z}
        a2x: {self.a2x}
        a2y: {self.a2y}
        a2z: {self.a2z}
        a3x: {self.a3x}
        a3y: {self.a3y}
        a3z: {self.a3z}
        a4x: {self.a4x}
        a4y: {self.a4y}
        a4z: {self.a4z}
        a5x: {self.a5x}
        a5y: {self.a5y}
        a5z: {self.a5z}
        a6x: {self.a6x}
        a6y: {self.a6y}
        a6z: {self.a6z}
        """


@dataclasses.dataclass
class ArmPose:
    x: float
    y: float
    z: float
    roll: float
    pitch: float
    yaw: float

    tool_pos: float = 90

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        roll: float,
        pitch: float,
        yaw: float,
        degree: bool = False,
    ) -> None:
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
    def as_tuple(self) -> Tuple[float, float, float, float, float, float]:
        return (self.x, self.y, self.z, self.roll, self.pitch, self.yaw)

    @property
    def as_list(self) -> List[float]:
        return list(self.as_tuple)

    @property
    def as_dict(self) -> Dict[str, float]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
        }


"""
    ----------------------------------------
                    ArmKinematics
    ----------------------------------------
"""


class ArmKinematics:
    def __init__(self, arm_parameters: ArmParameters) -> None:
        self.arm_params: ArmParameters = arm_parameters

    class NotReachableError(Exception):
        def __init__(self, message: str, angles: Optional[List[float]]) -> None:
            super().__init__(message)
            self.angles: Optional[List[float]] = angles
            self.message: str = message

    def angles_to_pose(self, angles: List[float]) -> ArmPose:
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

    def pose_to_angles(self, target_pose: ArmPose, current_angles: List[float]) -> Optional[List[float]]:
        try:
            found_angles = self._pose_to_angles(target_pose, current_angles)
            return found_angles
        except self.NotReachableError as exception:
            console.log(f"NotReachableError in pose_to_angles: {exception}", style="error")
            return None

    def _pose_to_angles(self, target_pose: ArmPose, current_angles: Optional[List[float]] = None) -> List[float]:
        if current_angles is None:
            current_angles = [0 for _ in range(len(self.arm_params.joints))]

        prev_angles = current_angles
        J1_prev = prev_angles[0]
        J4_prev = prev_angles[3]

        x, y, z, roll, pitch, yaw = target_pose.as_tuple

        TCP = np.array([[x], [y], [z]])
        xdirection = create_rotation_matrix_from_euler_angles(roll, pitch, yaw) @ np.array([[1], [0], [0]])

        WP = TCP - self.arm_params.a6x * xdirection
        # Finding J1,J2,J3

        J1 = np.arctan2(WP[1, 0], WP[0, 0])

        if WP[0, 0] == 0 and WP[1, 0] == 0:
            J1 = J1_prev
        WPxy = np.sqrt(WP[0, 0] ** 2 + WP[1, 0] ** 2)
        L = WPxy - self.arm_params.a2x
        H = WP[2, 0] - self.arm_params.a1z - self.arm_params.a2z
        P = np.sqrt(H**2 + L**2)
        b4x = np.sqrt(self.arm_params.a4z**2 + (self.arm_params.a4x + self.arm_params.a5x) ** 2)
        if (P <= self.arm_params.a3z + b4x) and abs(self.arm_params.a3z - b4x) < P:
            alfa = np.arctan2(H, L)
            cosbeta = (P**2 + self.arm_params.a3z**2 - b4x**2) / (2 * P * self.arm_params.a3z)
            beta = np.arctan2(np.sqrt(1 - cosbeta**2), cosbeta)
            cosgamma = (self.arm_params.a3z**2 + b4x**2 - P**2) / (2 * self.arm_params.a3z * b4x)
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
            return [nearest_by_2pi_ref(angle, ref) for angle, ref in zip(found_angles, prev_angles)]
        raise self.NotReachableError("Target pose is not reachable", angles=prev_angles)
