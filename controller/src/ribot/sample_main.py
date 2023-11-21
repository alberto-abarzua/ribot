from ribot.control.arm_kinematics import ArmParameters, ArmPose
from ribot.controller import ArmController, Settings
from ribot.utils.prints import console

if __name__ == "__main__":
    console.log("Starting sample_main.py!", style="bold green")
    EPSILON = 0.01

    # Arm parameters (Physical dimensions of the arm)
    arm_params: ArmParameters = ArmParameters()
    arm_params.a2x = 0
    arm_params.a2z = 172.48

    arm_params.a3z = 173.5

    arm_params.a4z = 0
    arm_params.a4x = 126.2

    arm_params.a5x = 64.1
    arm_params.a6x = 169

    controller = ArmController(arm_parameters=arm_params)
    # The websocket server is used by the simulation in the Frontend
    controller.start(websocket_server=False, wait=True)

    controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 400)
    controller.home()

    # Move to a position
    position = ArmPose(x=320, y=0, z=250, pitch=0, roll=0, yaw=0)
    controller.move_to(position)
    controller.wait_done_moving()

    # Move to angles (rads)
    angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    controller.move_joints_to(angles)

    # Move the tool (rads)
    controller.set_tool_value(1.2)

    print("Arm was homed?", controller.is_homed)
