---
title: QuickStart
description: Fast guide to get started with the ribot-controller python library to control the robot arm
sidebar_position: 1
keywords: [ribot, robotic arm, python, control library, armcontroller]
---

# QuickStart

The backend of ribot is written in python, and uses the ribot-controller library to control the robot arm.

This Library can also be used in a standalone project, given that you have the hardware and
the esp flashed correctly to look for the server and connect to it.

## Installation

To install the library just run

```bash
pip install ribot-controller
```

## Usage

Here we have a quick example of how to use the library to control the robot arm

As you can see we first import the library and then we create an instance of the controller
with the arm parameters, then we start the controller and set the settings for the joints
and home the robot arm.

Then we can move the robot arm to a position or to a set of angles, we can also set the tool value
and check if the robot arm is homed.

```python
from ribot.control.arm_kinematics import ArmParameters, ArmPose
from ribot.controller import ArmController, Settings

if __name__ == "__main__":
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

    print("Homed:", controller.is_homed)

```
