# 6DOF 3D printeable Robot Arm

# Brief summary 
<p> This project consists of a 3D printable (designed in Fusion 360) Robot Arm with six degrees of freedom. This arm is controlled using an Arduino Mega which controlls all the stepper motors that move the arm's joints. The arduino is controlled with a python script that runs it through serial comunication. All the kinematics and movements of the robot are coded in Python.
</p>

<p>Usefull things to know:</p>

- TCP: Tool at the end of the robot arm also known as end effector
- The state of the TCP can be described by a position with 3 coordinates (x,y,z) and 3 angles
roll, pitch and yaw also known as euler angles.
- A certain TCP state can be achieved with multiple angle configurations of each joint. (Inverse Kinematics can have multiple solutions)
- A certain angle configurations of the joints can only achieve one TCP state.

## Photos and videos of the arm and it's evolution.

### First robot arm (4DOF) using servo motors and Arduino Uno
![First robot arm (4DOF) using servo motors and Arduino Uno](https://i.ibb.co/C0yTw15/servo-arm-1.jpg)



### Current version of the arm using stepper motors and Arduino Mega.
![Whole view](https://i.ibb.co/4WtFVFL/8-E2-F34-B1-2-A22-40-E4-8-CC6-2-BCDFD35-D6-A7.jpg)
Video of the current version of the arm working:
<https://youtu.be/Nz6M56jV3Vw>

### About arduino (C\C++) and design:
<p> The arduino code receives commands through serial comunication to control the steppers for each joint and the servo motor
    of the robot's gripper. There are multiple commands to move the robot these are defined and explained in the arduino code.</p>
    
<p>The arm displayed in the last photo was built using the following main components:</p>

- 2 x Nema 23 Stepper motors
- 5 x Various sizes of Nema 17 Stepper motors
- Arduino Mega 2560
- 24V power supply
- 7 x TB6600 stepper motor driver.
- 6 x hall effect sensors (Used to home each Joint)
- MG995 servo motor (Part of the robot's tool)

## About the Python Code.

<p> In terms of programing and maths the most complex parts of the project are solved here. Some of these are:</p>

- Direct Kinematics: This is the mathematical process of calculating the robot's TCP position (x,y,z,roll,pitch,yaw) based on the angles of each joint. (Code in armUtils/robotarm.py)

- Inverse Kinematics: This is the mathematical process of calculating the angles that every joint should have so that the TCP reaches a certain position (x,y,z) with certain angles (roll,pitch,yaw). (Code in armUtils/robotarm.py)
- 
- Simulation of the robot arm using openGL (arm_simulation.py), this is a keyboard controlled simulated version of the robot arm (6DOF stepper motor) shown in the previous photos. (Code in Main/arm_simulation.py). This part of the code uses the library "grafica" from <https://github.com/ivansipiran/grafica>. This is the GitHub repository used in the course "CC3501-Modelación y Computación Gráfica para Ingenieros" which is part of the study plan for "Licenciatura en Ciencias de la Ingeniería, Mención Computación v5- Universidad de Chile".    

![Simulation](https://i.ibb.co/xCFvBVg/2021-11-19-15-19-43-Settings.png)

<p>If an arduino with the correct code uploaded to it is conected to a COM port, the simulation can send the movements to it. To run the simulation with a real arduino use the next command inside the "Python Code" directory:</p>

    `python arm_simulation.py <port>` // Run simulation to an arduino
    `python arm_simulation.py` // Just run a simulation
    
    Requirements:

    Python 3.8.2

    Libraries installation:

     `pip install numpy scipy matplotlib pyopengl glfw ipython jupyter pillow imgui[glfw]`

