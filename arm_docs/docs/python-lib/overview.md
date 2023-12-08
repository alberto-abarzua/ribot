---
title: The Control Library
description: A Main Overview of the control library
sidebar_position: 2
---

# Main Overview of the Control Library

The RiBot control library is thoughtfully crafted to be minimalistic and user-friendly. It simplifies the complex task of controlling a robotic arm by offering a limited yet efficient set of objects and methods. The library's design in Python, with significant utilization of the typing module, ensures the code is both easy to understand and use.

## ArmParameters

A critical component of the library is `ArmParameters`. This class holds the physical dimensions of the robotic arm, essential for calculating both the forward and inverse kinematics. These dimensions are measured in millimeters (mm) for length and radians for angles, maintaining a standard unit system across the library.

### Defining ArmParameters

```python
from ribot.control.arm_kinematics import ArmParameters

# Creating an instance with dimensions in mm
arm_params: ArmParameters = ArmParameters()

# Setting up the dimensions
arm_params.a2x = 0
arm_params.a2z = 172.48
arm_params.a3z = 173.5
arm_params.a4z = 0
arm_params.a4x = 126.2
arm_params.a5x = 64.1
arm_params.a6x = 169
```

In this snippet, each parameter (`a2x`, `a2z`, `a3z`, etc.) represents a specific dimension of the robotic arm. These parameters are crucial for the kinematic algorithms that calculate the arm's movements.

### Configuring Range of Motion for Joints

```python
arm_params.joints[0].set_bounds(-1.0, 1.0)  # Setting bounds for Joint 1
```

The `set_bounds` method of the `Joint` object is used to define the range of motion for each joint. By specifying minimum and maximum values (`min_val` and `max_val`), you ensure that the arm's movements stay within these bounds, which is particularly important for maintaining the mechanical integrity of the robot and for accurate inverse kinematics calculations.

This approach to defining the physical characteristics and limitations of the robotic arm offers a streamlined yet powerful way to control its movements, ensuring that the arm operates within its mechanical constraints while performing tasks.

:::info

All measurements are in `mm` and angles `rads`

:::

## Overview of ArmPose and ArmController in RiBot Control Library

### ArmPose

`ArmPose` is a pivotal data structure in the RiBot control library, designed as a Python dataclass. It encapsulates the position and orientation of the robot arm in a structured format.

#### Fields of ArmPose

`ArmPose` includes six fields:

-   `x`, `y`, `z`: These represent the Cartesian coordinates of the robot arm's end-effector in space.
-   `roll`, `pitch`, `yaw`: These fields denote the orientation of the end-effector, using the roll-pitch-yaw (RPY) angles, which are a common way to represent 3D rotations.

#### Creating an ArmPose Instance

```python
from ribot.control.arm_kinematics import ArmPose

# Defining a pose with specific coordinates and orientation
pose = ArmPose(x=320, y=0, z=250, pitch=0, roll=0, yaw=0)
```

This instance of `ArmPose` can be used to instruct the robotic arm to move to the specified position and orientation, leveraging the inverse kinematics calculations of the system.

### ArmController

The `ArmController` is the central object in the RiBot control library, functioning as the interface through which users interact with the robotic arm.

#### Creating and Starting ArmController

```python
from ribot.controller import ArmController

# Initialize the controller with the arm's physical parameters
controller = ArmController(arm_parameters=arm_params)

# Start the controller without a WebSocket server
controller.start(websocket_server=False, wait=True)
```

This initialization process involves passing the physical dimensions (ArmParameters) to the controller, which are critical for accurate control and movement calculations.

#### Configuring and Controlling the Arm

```python
# Setting joint-specific settings, like steps per revolution
controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 400)

# Homing the robotic arm
controller.home()

# Instructing the arm to move to a specific position
controller.move_to(position)
controller.wait_done_moving()

# Moving the joints to specified angles (in radians)
controller.move_joints_to(angles)

# Adjusting the tool's position (in radians)
controller.set_tool_value(1.2)
```

In these snippets, the controller is used to configure the robot arm, move it to desired positions and orientations, and adjust the tool attached to the arm. The `home()` method is particularly important as it brings the robot arm to a known reference position, which is a crucial step in robotic control systems.

The `ArmController` serves as a comprehensive interface for controlling the robotic arm, with methods that facilitate movement to specific positions, adjusting joint angles, setting tool values, and executing the homing procedure. Its design ensures a seamless interaction between the user commands and the physical movements of the robotic arm.

## Settings in the RiBot Control Library

The RiBot control library allows for comprehensive customization of the robot arm's behavior through its settings functionality. These settings can be configured for each joint individually or set globally for the entire arm. This flexibility is crucial for optimizing the performance of the robot arm based on its specific hardware and application requirements.

### Settings Overview

Settings are stored in the `Settings` enum, encapsulating various parameters that dictate the operation of the robot arm. These settings can be applied using the `set_setting_joints` method of the `ArmController`.

#### The Settings Enum

```python
class Settings(Enum):
    HOMING_DIRECTION = 1
    SPEED_RAD_PER_S = 5
    STEPS_PER_REV_MOTOR_AXIS = 9
    CONVERSION_RATE_AXIS_JOINTS = 13
    HOMING_OFFSET_RADS = 17
    DIR_INVERTED = 31
```

Each setting in the `Settings` enum serves a specific purpose:

-   `HOMING_DIRECTION`: Specifies the direction the arm moves during the homing process. It can be either 1 (positive direction) or -1 (negative direction).
-   `SPEED_RAD_PER_S`: Determines the speed of the joint in radians per second.
-   `STEPS_PER_REV_MOTOR_AXIS`: Sets the number of steps the motor takes per full revolution.
-   `CONVERSION_RATE_AXIS_JOINTS`: The ratio used for converting movements between the motor axis and the robotic joint.
-   `HOMING_OFFSET_RADS`: Defines an offset from the homing position in radians.
-   `DIR_INVERTED`: Indicates whether the direction of the joint movement is inverted (1 for normal, -1 for inverted).

### Applying Settings to a Specific Joint

You can apply settings to individual joints as needed. For example, configuring joint 1 with specific parameters:

```python
from ribot.controller import Settings

# Configuring settings for joint 1
controller.set_setting_joint(Settings.HOMING_DIRECTION, 1, joint_idx=0)
controller.set_setting_joint(Settings.STEPS_PER_REV_MOTOR_AXIS, 400, joint_idx=0)
controller.set_setting_joint(Settings.SPEED_RAD_PER_S, 0.35, joint_idx=0)
controller.set_setting_joint(Settings.CONVERSION_RATE_AXIS_JOINTS, 9.7, joint_idx=0)
controller.set_setting_joint(Settings.HOMING_OFFSET_RADS, 0.4, joint_idx=0)
```

In this snippet, each line applies a specific setting to joint 1 (indexed as 0), including homing direction, speed, steps per revolution, conversion rate, and homing offset.

### Setting Global Parameters

Global settings apply to all joints of the robot arm. For instance, setting a uniform speed for all joints:

```python
# Setting a global speed for all joints
controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.35)
```

This functionality is particularly useful for synchronizing joint movements or establishing a baseline behavior for the robot arm.

The settings mechanism in the RiBot control library offers a detailed level of control, enabling precise tuning of the robotic arm's performance and behavior. By adjusting these settings, users can ensure that the arm operates optimally for a wide range of tasks, from delicate operations to tasks requiring speed and strength.
