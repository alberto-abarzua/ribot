import os

import numpy as np
from fastapi import Depends
from robot_arm_controller.control.arm_kinematics import ArmParameters
from robot_arm_controller.controller import ArmController, SingletonArmController


def get_controller() -> ArmController:
    initialized = SingletonArmController.was_initialized()
    if not initialized:
        # TODO: MOVE THIS TO A CONFIG FILE
        arm_params: ArmParameters = ArmParameters()
        arm_params.a2x = 0
        arm_params.a2z = 172.48

        arm_params.a3z = 173.5

        arm_params.a4z = 0
        arm_params.a4x = 126.2

        arm_params.a5x = 64.1
        arm_params.a6x = 169

        arm_params.j1.set_bounds(-np.pi / 2, np.pi / 2)
        arm_params.j2.set_bounds(-1.39626, 1.57)
        arm_params.j3.set_bounds(-np.pi / 2, np.pi / 2)
        arm_params.j5.set_bounds(-np.pi / 2, np.pi / 2)

        websocket_port = int(os.environ.get("CONTROLLER_WEBSOCKET_PORT", 8600))
        server_port = int(os.environ.get("CONTROLLER_SERVER_PORT", 8500))
        SingletonArmController.create_instance(
            arm_parameters=arm_params,
            websocket_port=websocket_port,
            server_port=server_port,
        )

    return SingletonArmController.get_instance()


controller_dependency = Depends(get_controller)
