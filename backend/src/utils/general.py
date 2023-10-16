import os
from pathlib import Path

import numpy as np
import toml
from fastapi import Depends
from robot_arm_controller.control.arm_kinematics import ArmParameters
from robot_arm_controller.controller import (
    ArmController,
    Settings,
    SingletonArmController,
)

PARENT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PARENT_DIR / "config" / "main_arm.toml"


PRINT_DEBUG = True


def get_controller() -> ArmController:
    initialized = SingletonArmController.was_initialized()

    if not initialized:
        # contents = toml.load(CONFIG_FILE)
        # arm_params: ArmParameters = ArmParameters()
        websocket_port = int(os.environ.get("CONTROLLER_WEBSOCKET_PORT", 8600))
        # params = contents["arm_parameters"]
        # for key in params:
        #     params[key] = float(params[key])
        #     arm_params.__setattr__(key, params[key])

        # # TODO: MOVE THIS TO A CONFIG FILE
        # arm_params.a2x = 0
        # arm_params.a2z = 172.48

        # arm_params.a3z = 173.5

        # arm_params.a4z = 0
        # arm_params.a4x = 126.2

        # arm_params.a5x = 64.1
        # arm_params.a6x = 169

        # arm_params.j1.set_bounds(-np.pi / 2, np.pi / 2)
        # arm_params.j2.set_bounds(-1.39626, 1.57)
        # arm_params.j3.set_bounds(-np.pi / 2, np.pi / 2)
        # arm_params.j5.set_bounds(-np.pi / 2, np.pi / 2)

        arm_params: ArmParameters = ArmParameters()
        websocket_port = int(os.environ.get("CONTROLLER_WEBSOCKET_PORT", 8600))
        server_port = int(os.environ.get("CONTROLLER_SERVER_PORT", 8500))

        SingletonArmController.create_instance(
            arm_parameters=arm_params,
            websocket_port=websocket_port,
            server_port=server_port,
        )

    return SingletonArmController.get_instance()


def start_controller() -> None:
    controller = get_controller()
    controller.start(wait=True)
    controller.print_status = PRINT_DEBUG
    controller.configure_from_file(CONFIG_FILE)


def stop_controller() -> None:
    controller = get_controller()
    controller.stop()


controller_dependency = Depends(get_controller)
