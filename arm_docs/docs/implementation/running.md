---
title: Running RiBot
description: Running the RiBot Server and Using the Web Interface
sidebar_position: 3
keywords: [ribot, robotic arm, python, control library, armcontroller]
---

# Running RiBot

Once your robotic arm is properly set up and flashed with the correct controller host and Wi-Fi information, you can begin operating it using RiBot. Here's a step-by-step guide to running the server and utilizing the web interface.

## Running the Server

To initiate the server, execute the following command:

```bash
python ribot.py runserver --esp
```

This command starts all necessary services for operation and launches the web control interface on port 3000.

-   **Accessing Locally**: If you are running the server on your local machine, access the web interface at [http://localhost:3000](http://localhost:3000).
-   **Accessing Remotely**: If you are running the server on a different machine, use that machine's IP address followed by `:3000` to access the web interface.

Once the server is running, you can interact with the robotic arm through the web interface, which includes three main sections:

## The Action List

The Action List is where you can build and manage routines for the robotic arm. It allows you to add various actions, create sequences, and execute them. The types of actions include:

-   **Move**: Directs the robot arm to a specific position.
-   **Wait**: Pauses the operation for a set duration.
-   **Tool**: Adjusts the tool (e.g., gripper) angle or position.
-   **Action Set**: A sequence of actions that can be executed in order, useful for repetitive tasks.

You can modify the action list by duplicating, deleting, or dragging actions to rearrange them. Clicking on an action allows you to edit its parameters. Additionally, action sequences can be downloaded for future use and uploaded by dragging and dropping them into the action list.

## The Free Control

The Free Control section provides an interactive interface for real-time control of the robot arm. It offers two modes:

-   **Joint Controls**: Allows you to move each joint of the robot arm independently.
-   **Cartesian Controls**: Enables movement of the robot arm in Cartesian space using X, Y, Z coordinates, and adjusting the roll, pitch, and yaw angles.

## The Visualization

This section features a Unity-based visualization of the robot arm. While primarily for entertainment and visual reference, it offers a virtual representation of the robot arm's movements.

By utilizing these features, you can effectively control your robotic arm, create complex routines, and visually track its movements. Whether for education, experimentation, or practical applications, RiBot provides a comprehensive and user-friendly platform for robotic arm manipulation and control.


## RiBot Controls

<div class="flex items-center justify-center gap-3 bg-gray-400 bg-opacity-30 rounded-md p-4">
    <img class="w-1/2 rounded-md" src="/img/docs/move_axis.gif" alt="RiBot Controls" width="100%" height="auto" />
    <img class="w-1/3 rounded-md" src="/img/docs/controls.png" alt="RiBot Controls" width="100%" height="auto" />
</div>

## The Action List

<div class="flex items-center justify-center gap-3 bg-gray-400 bg-opacity-30 rounded-md p-4">
    <img class="w-1/2 rounded-md" src="/img/docs/actions.gif" alt="RiBot Controls" width="100%" height="auto" />
    <img class="w-[45%] rounded-md" src="/img/docs/run_actions.gif" alt="RiBot Controls" width="100%" height="auto" />
</div>

