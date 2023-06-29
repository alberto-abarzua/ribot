import threading
import time

import numpy as np

from control.arm_kinematics import ArmKinematics, ArmParameters
from control.controller_servers import ControllerServer, WebsocketServer
from utils.messages import Message
from utils.prints import console


class ArmController:
    def __init__(self):
        self._current_angles = [0, 0, 0, 0, 0, 0]
        self.num_joints = len(self._current_angles)
        self.move_queue_size = 0
        self.is_homed = False

        self.current_angles_lock = threading.Lock()
        self.controller_server = ControllerServer(self, 8500)
        self.websocket_server = WebsocketServer(65433, self)

        # register new handlers here
        self.message_op_handlers = {
            "M": self.handle_move_message,
            "S": self.handle_status_message,
            "C": self.handle_config_message,
        }

        # Arm parameters
        self.arm_params = ArmParameters()
        self.arm_params.a2x = 0
        self.arm_params.a2z = 172.48

        self.arm_params.a3z = 173.5

        self.arm_params.a4z = 0
        self.arm_params.a4x = 126.2

        self.arm_params.a5x = 64.1
        self.arm_params.a6x = 169

        self.arm_params.j1.set_bounds(-np.pi / 2, np.pi / 2)
        self.arm_params.j2.set_bounds(-1.39626, 1.57)
        self.arm_params.j3.set_bounds(-np.pi / 2, np.pi / 2)
        self.arm_params.j5.set_bounds(-np.pi / 2, np.pi / 2)

        self.kinematics = ArmKinematics(self)

        self.command_cooldown = 0.01

    """
    ----------------------------------------
                    General Methods
    ----------------------------------------
    """

    def start(self):
        console.print("Starting controller", style="setup")
        self.websocket_server.start()
        self.controller_server.start()

    def stop(self):
        console.print("Stopping controller", style="setup")
        self.websocket_server.stop()
        self.controller_server.stop()

    @property
    def current_angles(self):
        with self.current_angles_lock:
            return self._current_angles

    @current_angles.setter
    def current_angles(self, angles):
        if len(angles) != self.num_joints:
            raise ValueError(f"Angles must be a list of length {self.num_joints}")
        with self.current_angles_lock:
            self._current_angles = angles

    @property
    def is_ready(self):
        websocket_server_up = self.websocket_server.is_ready
        controller_server_up = self.controller_server.is_ready
        return websocket_server_up and controller_server_up

    """
    ----------------------------------------
                    Handlers
    ----------------------------------------
    """

    def handle_move_message(self, message):
        console.print(f"Received move message: {message}", style="info")

    def handle_status_message(self, message):
        code = message.code
        if code == 1:
            angles = message.args[: self.num_joints]
            self.current_angles = angles
            self.move_queue_size = message.args[self.num_joints]
            self.is_homed = message.args[self.num_joints + 1]

        console.print(f"Received status message: {message}", style="info")

    def handle_config_message(self, message):
        console.print(f"Received config message: {message}", style="info")

    """
    ----------------------------------------
                    API Methods -- MOVE
    ----------------------------------------
    """

    def move_to_angles(self, angles):
        if not self.is_homed:
            console.print("Arm is not homed", style="error")
            return
        message = Message("M", 1, angles)
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)

    def move_to_pose(self, pose):
        target_angles = self.kinematics.pose_to_angles(pose)
        self.move_to_angles(target_angles)
        time.sleep(self.command_cooldown)

    def home(self, wait=False):
        message = Message("M", 3)
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)
        if wait:
            while not self.is_homed:
                time.sleep(0.1)

    def home_joint(self, joint_idx):
        message = Message("M", 5, [joint_idx])
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)

    """
    ----------------------------------------
                    API Methods -- STATUS
    ----------------------------------------
    """

    def health_check(self):
        if not self.is_ready:
            console.print("Not connected", style="error")
            return False
        message = Message("S", 3)
        self.controller_server.send_message(message, mutex=True)
        message = self.controller_server.receive_message(mutex=True, timeout=3)
        if message is None:
            console.print("No response", style="error")
            return False
        if message.op == b"S" and message.code == 4:
            console.print("Health check passed", style="success")
            return True

        return False

    """
    ----------------------------------------
                    API Methods -- CONFIG
    ----------------------------------------
    """
