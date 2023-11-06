import os
from pathlib import Path

from fastapi import Depends
from robot_arm_controller.control.arm_kinematics import ArmParameters
from robot_arm_controller.controller import ArmController, SingletonArmController

PARENT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PARENT_DIR / "config" / "main_arm.toml"


PRINT_DEBUG = True


def get_controller() -> ArmController:
    initialized = SingletonArmController.was_initialized()

    if not initialized:
        websocket_port = int(os.environ.get("CONTROLLER_WEBSOCKET_PORT", 8600))

        arm_params: ArmParameters = ArmParameters()
        websocket_port = int(os.environ.get("CONTROLLER_WEBSOCKET_PORT", 8600))
        server_port = int(os.environ.get("CONTROLLER_SERVER_PORT", 8500))

        SingletonArmController.create_instance(
            arm_parameters=arm_params,
            websocket_port=websocket_port,
            server_port=server_port,
            config_file=CONFIG_FILE,
            print_status=PRINT_DEBUG,
        )

    return SingletonArmController.get_instance()


def start_controller() -> None:
    controller = get_controller()
    controller.start()


def stop_controller() -> None:
    controller = get_controller()
    controller.stop()


controller_dependency = Depends(get_controller)
