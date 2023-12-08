---
title: The ArmController Class
description: Detailed information about the methods of the ArmController class.
sidebar_position: 3
keywords: [ribot, robotic arm, python, control library, armcontroller]
---

# The ArmController Class

The `ArmController` class in the RiBot control library is a comprehensive interface for controlling and managing the robotic arm. It encapsulates a range of functionalities from basic movement to complex settings adjustments, making it a central component for robotic arm manipulation.

## Fields

The `ArmController` class contains several fields that store the current state and configuration of the robotic arm:

- `current_pose: ArmPose`: Stores the current position and orientation of the robotic arm.
- `current_angles: List[float]`: Holds the current angles of each joint in the arm.
- `is_homed: bool`: Indicates whether the robotic arm has been homed.
- `status: ControllerStatus`: Reflects the current status of the controller, which can be NOT_STARTED, WAITING_CONNECTION, RUNNING, or STOPPED.
- `tool_value: float`: The current value (position/angle) of the tool attached to the arm.
- `arm_params: ArmParameters`: Contains the physical parameters of the robotic arm.

## Methods

### General

These methods provide basic control over the robotic arm:

- `start(wait: bool = False, websocket_server: bool = True) -> None`: Starts the controller, optionally waiting until it's fully operational and deciding whether to start a WebSocket server.
- `stop() -> None`: Stops the controller.
- `home(wait: bool = True) -> None`: Homes the robotic arm, optionally waiting until the homing process is complete.
- `home_joint(joint_idx: int) -> None`: Homes a specific joint of the robotic arm.

### Movement

These methods control the movement of the robotic arm:

- `move_to(pose: ArmPose) -> bool`: Moves the arm to a specified pose.
- `move_to_relative(pose: ArmPose) -> bool`: Moves the arm to a pose relative to its current position.
- `move_joints_to(angles: List[float]) -> bool`: Moves the joints of the arm to specified angles.
- `move_joints_to_relative(angles: List[float]) -> bool`: Moves the joints of the arm to angles relative to their current positions.
- `move_joint_to(joint_idx: int, angle: float) -> bool`: Moves a specific joint to a specified angle.
- `move_joint_to_relative(joint_idx: int, angle: float) -> bool`: Moves a specific joint to an angle relative to its current position.
- `valid_pose(pose: ArmPose) -> bool`: Checks if a given pose is valid for the robotic arm.
- `wait_done_moving() -> None`: Waits until the arm has finished moving.

### Tool

- `set_tool_value(value: float) -> bool`: Sets the value (position/angle) of the tool.

### Settings

:::info

More info on the settings enum can be found [here](/docs/python-lib/overview#settings-in-the-ribot-control-library).

:::

These methods are used to configure settings for individual joints or the entire arm:

- `set_setting_joint(setting_key: Settings, value: float, joint_idx: int) -> None`: Sets a specific setting for a joint.
- `set_setting_joints(setting_key: Settings, value: float) -> None`: Sets a specific setting for all joints.
- `get_setting_joint(setting_key: Settings, joint_idx: int) -> float`: Retrieves a specific setting from a joint.
- `get_setting_joints(setting_key: Settings) -> List[float]`: Retrieves specific settings from all joints.

Additional methods to configure joint drivers and endstops:

- `set_joint_driver_stepper(joint_idx: int, step_pin: int, dir_pin: int) -> None`: Configures a stepper motor driver for a joint.
- `set_joint_driver_servo(joint_idx: int, pin: int) -> None`: Configures a servo motor driver for a joint.
- `set_joint_endstop_hall(joint_idx: int, pin: int) -> None`: Sets a hall sensor endstop for a joint.
- `set_joint_endstop_none(joint_idx: int) -> None`: Configures a joint with no endstop.
- `set_tool_driver_servo(pin: int) -> None`: Sets the tool's driver as a servo with a specified pin.

The `ArmController` class, with its diverse range of fields and methods, serves as the backbone for controlling and customizing the robotic arm's operations, catering to a variety of tasks and applications.
