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
        self.last_health_check = 0

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

    def start(self, wait=True, websocket_server=True):
        console.print("Starting controller", style="setup")
        if websocket_server:
            self.websocket_server.start()
        else:
            self.websocket_server = None
        self.controller_server.start()
        start_time = time.time()
        if wait:
            while not self.is_ready:
                time.sleep(0.1)
                if time.time() - start_time > 10:
                    raise TimeoutError("Controller took too long to start, check arm client")
        console.print("\nController Started!", style="setup")

    def stop(self):
        console.print("Stopping controller...", style="setup", end="\n")
        if self.websocket_server is not None:
            self.websocket_server.stop()
        self.controller_server.stop()
        console.print("Controller Stopped", style="setup")

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
        if self.websocket_server is None:
            websocket_server_up = True
        else:
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
        if code == 4:
            self.last_health_check = time.time()
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
        self.move_queue_size += 1

    def move_to(self, pose):
        target_angles = self.kinematics.pose_to_angles(pose)
        self.move_to_angles(target_angles)

    def home(self, wait=True):
        message = Message("M", 3)
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)
        start_time = time.time()
        self.is_homed = False
        if wait:
            while not self.is_homed:
                time.sleep(0.1)
                if time.time() - start_time > 60:
                    raise TimeoutError("Arm took too long to home")
            # wait for angles to get to 0
            start_time = time.time()

            while not all([abs(angle) < 0.1 for angle in self.current_angles]):
                time.sleep(0.1)
                if time.time() - start_time > 60:
                    raise TimeoutError("Arm took too long to home")

    def home_joint(self, joint_idx):
        message = Message("M", 5, [joint_idx])
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)

    def wait_queue_empty(self):
        while self.move_queue_size > 0:
            time.sleep(0.1)

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
        current_time = time.time()
        with self.controller_server.connection_mutex:
            self.controller_server.send_message(message)
        while self.last_health_check < current_time and time.time() - current_time < 5:
            time.sleep(0.01)

        return self.last_health_check > current_time

    """
    ----------------------------------------
                    API Methods -- CONFIG
    ----------------------------------------
    """

    def set_homing_direction(self, direction):
        message = Message("C", 1, [direction])
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)
