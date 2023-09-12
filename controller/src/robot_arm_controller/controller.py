import dataclasses
import time
from enum import Enum
from typing import Callable, Dict, List, Optional

import numpy as np

from robot_arm_controller.control.arm_kinematics import (
    ArmKinematics,
    ArmParameters,
    ArmPose,
)
from robot_arm_controller.control.controller_servers import (
    ControllerServer,
    FIFOLock,
    WebsocketServer,
)
from robot_arm_controller.utils.messages import Message, MessageOp
from robot_arm_controller.utils.prints import console


class Settings(Enum):
    HOMING_DIRECTION = 1
    SPEED_RAD_PER_S = 5
    STEPS_PER_REV_MOTOR_AXIS = 9
    CONVERSION_RATE_AXIS_JOINTS = 13
    HOMING_OFFSET_RADS = 17


@dataclasses.dataclass
class Setting:
    value: float
    code_set: int
    code_get: int
    last_updated: float = -1


class ArmController:
    def __init__(
        self,
        arm_parameters: ArmParameters,
        websocket_port: int = 8600,
        server_port: int = 8500,
    ) -> None:
        # Arm Status
        self._current_angles: List[float] = [0, 0, 0, 0, 0, 0]
        self.current_angles_lock: FIFOLock = FIFOLock()

        self.tool_value: float = 0
        self.move_queue_size: int = 0
        self.is_homed: bool = False
        self.last_health_check: float = 0

        self.controller_server: ControllerServer = ControllerServer(self, server_port)
        self.websocket_server: Optional[WebsocketServer] = WebsocketServer(self, websocket_port)

        self.arm_params = arm_parameters
        self.num_joints: int = len(self._current_angles)
        self.kinematics: ArmKinematics = ArmKinematics(self.arm_params)

        self.command_cooldown: float = 0.01
        self.connection_controller_timeout: int = 15

        self.joint_settings: List[Dict[Settings, Setting]] = []
        self.joint_settings_response_code: List[Dict[int, Setting]] = []

        # register new handlers here

        self.message_op_handlers: Dict[MessageOp, Callable[[Message], None]] = {
            MessageOp.MOVE: self.handle_move_message,
            MessageOp.STATUS: self.handle_status_message,
            MessageOp.CONFIG: self.handle_config_message,
        }

        for _ in range(self.num_joints):
            current_joint_settings = {
                Settings.HOMING_DIRECTION: Setting(value=1, code_set=1, code_get=3),
                Settings.SPEED_RAD_PER_S: Setting(value=1, code_set=5, code_get=7),
                Settings.STEPS_PER_REV_MOTOR_AXIS: Setting(value=200, code_set=9, code_get=11),
                Settings.CONVERSION_RATE_AXIS_JOINTS: Setting(value=1, code_set=13, code_get=15),
                Settings.HOMING_OFFSET_RADS: Setting(value=np.pi / 4, code_set=17, code_get=19),
            }
            self.joint_settings.append(current_joint_settings)
            self.joint_settings_response_code.append(
                {setting.code_get + 1: setting for setting in current_joint_settings.values()}
            )

    """
    ----------------------------------------
                    General Methods
    ----------------------------------------
    """

    def __str__(self) -> str:
        output = []
        output.append(f"Current Angles: {self._current_angles}")
        output.append(f"Tool Position: {self.tool_value}")
        output.append(f"Is Homed: {self.is_homed}")
        output.append(f"Queue Size: {self.move_queue_size}")

        return "\n".join(output)

    def start(self, wait: bool = True, websocket_server: bool = True) -> None:
        console.print("Starting controller!", style="setup")
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
    def current_pose(self) -> ArmPose:
        return self.kinematics.angles_to_pose(self.current_angles)

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

        return websocket_server_up and controller_server_up

    """
    ----------------------------------------
                    Handlers
    ----------------------------------------
    """

    def handle_move_message(self, message: Message) -> None:
        pass

    def handle_status_message(self, message: Message) -> None:
        code = message.code
        if code == 1:
            self.current_angles = message.args[: self.num_joints]
            self.tool_value = message.args[self.num_joints]
            self.move_queue_size = int(message.args[self.num_joints + 1])
            self.is_homed = message.args[self.num_joints + 2] == 1

        if code == 4:
            self.last_health_check = time.time()

    def handle_config_message(self, message: Message) -> None:
        code = message.code
        joint_idx = int(message.args[0])
        if code in self.joint_settings_response_code[joint_idx].keys():
            setting = self.joint_settings_response_code[joint_idx][code]
            setting.value = message.args[1]
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
        message = Message(MessageOp.MOVE, 1, angles)
        self.controller_server.send_message(message, mutex=True)
        self.move_queue_size += 1

    def move_to(
        self,
        pose: ArmPose,
    ) -> None:
        target_angles = self.kinematics.pose_to_angles(pose, self.current_angles)
        if target_angles is None:
            console.print("Target pose is not reachable", style="error")
            return
        self.move_to_angles(target_angles)

    def home(self, wait: bool = True) -> None:
        message = Message(MessageOp.MOVE, 3)
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
        message = Message(MessageOp.MOVE, 5, [joint_idx])
        self.controller_server.send_message(message, mutex=True)
        time.sleep(self.command_cooldown)

    def set_tool_value(self, angle: float) -> None:
        message = Message(MessageOp.MOVE, 7, [angle])
        self.controller_server.send_message(message, mutex=True)
        self.move_queue_size += 1

    def wait_until_angles_at_target(self, target_angles: List[float], epsilon: float = 0.01) -> None:
        while not np.allclose(self.current_angles, target_angles, atol=epsilon):
            time.sleep(0.01)

    def wait_done_moving(self) -> None:
        while self.move_queue_size > 0:
            time.sleep(0.01)

    """
    ----------------------------------------
                    API Methods -- STATUS
    ----------------------------------------
    """

    def health_check(self) -> bool:
        if not self.is_ready:
            console.print("Not connected", style="error")
            return False
        message = Message(MessageOp.STATUS, 3)
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

    def set_setting_joint(self, setting_key: Settings, value: float, joint_idx: int) -> None:
        if setting_key not in self.joint_settings[joint_idx].keys():
            raise ValueError(f"Invalid setting key for joint setting: {setting_key}")
        setting = self.joint_settings[joint_idx][setting_key]
        code = setting.code_set
        message = Message(MessageOp.CONFIG, code, [float(joint_idx), value])
        self.controller_server.send_message(message, mutex=True)
        setting.last_updated = -1

    def set_setting_joints(self, setting_key: Settings, value: float) -> None:
        for joint_idx in range(self.num_joints):
            self.set_setting_joint(setting_key, value, joint_idx)

    def get_setting_joint(self, setting_key: Settings, joint_idx: int) -> float:
        if setting_key not in self.joint_settings[joint_idx].keys():
            raise ValueError(f"Invalid setting key for joint setting: {setting_key}")

        setting = self.joint_settings[joint_idx][setting_key]
        code = setting.code_get

        if setting.last_updated < 0:  # valid value
            message = Message(MessageOp.CONFIG, code, [float(joint_idx)])
            self.controller_server.send_message(message, mutex=True)
            while setting.last_updated < 0:
                time.sleep(0.01)
        return setting.value

    def get_setting_joints(self, setting_key: Settings) -> List[float]:
        return [self.get_setting_joint(setting_key, joint_idx) for joint_idx in range(self.num_joints)]


class SingletonArmController:
    _instance: Optional[ArmController] = None

    @classmethod
    def create_instance(
        cls,
        arm_parameters: ArmParameters,
        websocket_port: int = 8600,
        server_port: int = 8500,
    ) -> None:
        cls._instance = ArmController(
            arm_parameters=arm_parameters, websocket_port=websocket_port, server_port=server_port
        )

    @classmethod
    def get_instance(cls) -> ArmController:
        if cls._instance is None:
            raise ValueError("ArmController has not been initialized")
        return cls._instance

    @classmethod
    def was_initialized(cls) -> bool:
        return cls._instance is not None
