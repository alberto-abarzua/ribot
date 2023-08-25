# 6DOF Robotic Arm Controller

## Overview

This is the Python server used to control a robotic arm that uses the firmware found in [this repository](https://github.com/alberto-abarzua/Robot-Arm-Control).

The controller forms the core of our system, housed within a Python script that is executed on a computer. The role of the controller is two-fold. It sends commands to the firmware, while simultaneously receiving data from it. As the primary interface for the user, it provides a programmable interface for the manipulation and operation of the robotic arm.

## Features

- [x] Basic control of the robotic arm using a Python script
- [x] Communication between controller and firmware via WiFi TCP socket
- [x] Implementing Inverse Kinematics for the robotic arm
- [x] Implementing Forward Kinematics for the robotic arm
- [x] Implementing a basic controller for the robotic arm
- [x] More details in main [repository](https://github.com/alberto-abarzua/Robot-Arm-Control).

## How to install

```bash
pip install robot-arm-controller
```