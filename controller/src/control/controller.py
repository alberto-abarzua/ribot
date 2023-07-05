import dataclasses
import time
from typing import Callable, Dict, List, Optional

import numpy as np

from control.arm_kinematics import ArmKinematics, ArmParameters, ArmPose
from control.controller_servers import ControllerServer, FIFOLock, WebsocketServer
from utils.messages import Message
from utils.prints import console


class ArmController:
    def __init__(self) -> None:
        self._current_angles: List[float] = [0, 0, 0, 0, 0, 0]
        self.num_joints: int = len(self._current_angles)
        self.move_queue_size: int = 0
        self.is_homed: bool = False
        self.last_health_check: float = 0

        self.current_angles_lock: FIFOLock = FIFOLock()
        self.controller_server: ControllerServer = ControllerServer(self, 8500)
        self.websocket_server: Optional[WebsocketServer] = WebsocketServer(65433, self)

        # register new handlers here
        self.message_op_handlers: Dict[str, Callable[[Message], None]] = {
            "M": self.handle_move_message,
            "S": self.handle_status_message,
            "C": self.handle_config_message,
        }

        # Arm parameters
        self.arm_params: ArmParameters = ArmParameters()
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

        self.kinematics: ArmKinematics = ArmKinematics(self.arm_params)

        self.command_cooldown: float = 0.01

        self.connection_controller_timeout: int = 15

        @dataclasses.dataclass
        class Setting:
            value: float
            code_set: int
            code_get: int
            last_updated: float = 0

        self.arm_settings: Dict[str, Setting] = {
            "homing_direction": Setting(value=1, code_set=1, code_get=3),  # 1 for positive, -1 for negative
            "speed_rad/s": Setting(value=1, code_set=5, code_get=7),  # speed in radians per second
            "steps_per_rev_motor_axis": Setting(
                value=200, code_set=9, code_get=11
            ),  # steps per revolution of motor axis (microstepping)
            "conversion_rate_axis_joints": Setting(
                value=1, code_set=13, code_get=15
            ),  # conversion rate from motor axis to joint angles
            "homing_offset_rads": Setting(
                value=np.pi / 4, code_set=17, code_get=19
            ),  # offset in radians for homing
        }

        self.settings_get_code_response_to_setting: Dict[int, Setting] = {
            setting.code_get + 1: setting for setting in self.arm_settings.values()
        }

    """
    ----------------------------------------
                    General Methods
    ----------------------------------------
    """

    def start(self, wait: bool = True, websocket_server: bool = True) -> None:
        console.print("Starting controller", style="setup")
        if websocket_server and self.websocket_server is not None:
            self.websocket_server.start()
        else:
            self.websocket_server = None
        self.controller_server.start()
        start_time = time.time()
        if wait:
            while not self.is_ready:
                time.sleep(0.1)
                if time.time() - start_time > self.connection_controller_timeout:
                    raise TimeoutError("Controller took too long to start, check arm client")
        console.print("\nController Started!", style="setup")

    def stop(self) -> None:
        console.print("Stopping controller...", style="setup", end="\n")
        if self.websocket_server is not None:
            self.websocket_server.stop()
        self.controller_server.stop()
        console.print("Controller Stopped", style="setup")

    @property
    def current_angles(self) -> List[float]:
        with self.current_angles_lock:
            return self._current_angles

    @current_angles.setter
    def current_angles(self, angles: List[float]) -> None:
        if len(angles) != self.num_joints:
            raise ValueError(f"Angles must be a list of length {self.num_joints}")
        with self.current_angles_lock:
            self._current_angles = angles

    @property
    def is_ready(self) -> bool:
        if self.websocket_server is None:
            websocket_server_up = True
        else:
            websocket_server_up = self.websocket_server.is_ready
        controller_server_up = self.controller_server.is_ready
        console.print(
            f"Websocket server up: {websocket_server_up}, controller server up: {controller_server_up}",
            style="info",
        )
        return websocket_server_up and controller_server_up

    """
    ----------------------------------------
                    Handlers
    ----------------------------------------
    """

    def handle_move_message(self, message: Message) -> None:
        console.print(f"Received move message: {message}", style="info")

    def handle_status_message(self, message: Message) -> None:
        code = message.code
        if code == 1:
            angles = message.args[: self.num_joints]
            self.current_angles = angles
            self.move_queue_size = int(message.args[self.num_joints])
            self.is_homed = message.args[self.num_joints + 1] == 1
        if code == 4:
            self.last_health_check = time.time()
        console.print(f"Received status message: {message}", style="info")

    def handle_config_message(self, message: Message) -> None:
        console.print(f"Received config message: {message}", style="info")
        code = message.code
        if code in self.settings_get_code_response_to_setting.keys():
            setting = self.settings_get_code_response_to_setting[code]
            setting.value = message.args[0]
            setting.last_updated = time.time()

    """
    ----------------------------------------
                    API Methods -- MOVE
    ----------------------------------------
    """

    def move_to_angles(self, angles: List[float]) -> None:
        if not self.is_homed:
            console.print("Arm is not homed", style="error")
            return
        message = Message("M", 1, angles)
        self.controller_server.send_message(message, mutex=True)
        self.move_queue_size += 1

    def move_to(self, pose: ArmPose) -> None:
        target_angles = self.kinematics.pose_to_angles(pose, self.current_angles)
        if target_angles is None:
            console.print("Target pose is not reachable", style="error")
            return
        self.move_to_angles(target_angles)

    def home(self, wait: bool = True) -> None:
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

    def home_joint(self, joint_idx: int) -> None:
        message = Message("M", 5, [joint_idx])
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)

    def wait_queue_empty(self) -> None:
        while self.move_queue_size > 0:
            time.sleep(0.1)

    """
    ----------------------------------------
                    API Methods -- STATUS
    ----------------------------------------
    """

    def health_check(self) -> bool:
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

    def set_setting_joint(self, setting_key: str, joint_idx: int, value: float) -> None:
        setting = self.arm_settings[setting_key]
        code = setting.code_set
        message = Message("C", code, [float(joint_idx), value])
        self.controller_server.send_message(message, mutex=True)
        setting.last_updated = -1

    def set_setting(self, setting_key: str, value: float) -> None:
        setting = self.arm_settings[setting_key]
        code = setting.code_set
        message = Message("C", code, [value])
        self.controller_server.send_message(message, mutex=True)
        setting.last_updated = -1
        setting.value = value

    def get_setting_joint(self, setting_key: str, joint_idx: int) -> float:
        setting = self.arm_settings[setting_key]
        code = setting.code_get
        message = Message("C", code, [float(joint_idx)])
        self.controller_server.send_message(message, mutex=True)
        setting.last_updated = -1
        # wait for setting to be updated
        while setting.last_updated < 0:
            time.sleep(0.01)

        return setting.value

    def get_setting(self, setting_key: str) -> float:
        setting = self.arm_settings[setting_key]
        code = setting.code_get
        message = Message("C", code)
        self.controller_server.send_message(message, mutex=True)
        setting.last_updated = -1
        # wait for setting to be updated
        while setting.last_updated < 0:
            time.sleep(0.01)

        return setting.value
