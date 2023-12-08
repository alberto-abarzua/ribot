---
title: Software Installation
description: Installation of the Robot Arm Software
sidebar_position: 2
keywords: [robot arm, software, installation, guide]
---

# Software Installation Guide for RiBot

## Requirements for Installation

Before installing RiBot, ensure that your system meets the following prerequisites:

- **Docker**: Install Docker Desktop for Windows or Mac, or Docker Engine if you are using a Raspberry Pi. You can download Docker Desktop from [here](https://www.docker.com/products/docker-desktop).

- **Python**: Your system should have Python version 3.8 or higher. Python is essential for running the RiBot scripts and interacting with the control system.

- **ESPtool**: This is a Python library needed for flashing the ESP32 microcontroller. Install it using the following command in your terminal:

    ```bash
    pip install esptool
    ```

## Steps to Install RiBot

Follow these steps to install RiBot on your system:

1. **Clone the RiBot Repository**:
   
   Begin by cloning the RiBot repository from GitHub. Open your terminal and enter:

    ```bash
    git clone https://github.com/alberto-abarzua/ribot.git
    ```

2. **Navigate to the Repository Folder**:
   
   Change your current directory to the RiBot repository:

    ```bash
    cd ribot
    ```

3. **Explore the Main Script**:
   
   The `ribot.py` script is the main control file for the robotic arm. To view all available options, run:

    ```bash
    python ribot.py --help
    ```

4. **Run a Simulation**:

   For a quick preview of RiBot with a simulated robot arm, execute:

    ```bash
    python ribot.py runserver
    ```

   This command starts a server on port 3000. To access the web interface, visit [http://localhost:3000](http://localhost:3000) in your web browser.

5. **Install on Your Robot Arm**:

   If you're satisfied with the simulation and want to install RiBot on your own robotic arm, there are additional steps to follow. For that check the [hardware section](/docs/category/hardware-implementation) of our documentation.

