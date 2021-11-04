# 6DOF 3D printeable Robot Arm

# Brief summary 
<p> This project consists of a 3D printable (designed in Fusion 360) Robot Arm with six degrees of freedom. This arm is controlled using an Arduino Mega which controlls all the stepper motors that move the arm's joints. The arduino is controlled from a python script that runs it through serial comunication. All the kinematics and movements of the robot are implemented in Python.
</p>

<p>Usefull things to know</p>

- TCP: Tool at the end of the robot arm also known as end effector
- The state of the TCP can be described by a position with 3 coordinates (x,y,z) and 3 angles
roll,pitch and yaw also known as euler angles.
- A certain TCP state can be achieved with multiple angle configurations of each joint. (Inverse Kinemaitcs can have multiple solutions)
- A certain angle configurations of the joints only can achieve one and only one TCP state.


<p> As this is a project in development, there are still things to improve. The previous iteration of the robot arm (design and 3D prints) had multiple flaws, most of them related to hardware issues (stepper motors, drivers and belts) due to these issues most of arm is going to be redesigned.
</p>

## Photos and videos of the arm and it's evolution.

### First robot arm (4DOF) using servo motors and Arduino Uno
![First robot arm (4DOF) using servo motors and Arduino Uno](https://i.ibb.co/C0yTw15/servo-arm-1.jpg)
Video with the arm working
<https://youtu.be/y-Uy8BWoXXg>

### Current version of the arm using stepper motors and Arduino Mega.
![Current version of the arm using servo motors.](https://ibb.co/QmV1JbF)
<p>
Not a really good test video but the current arm is disassembled and sadly y did not 
record any other viedo.
</p>

<https://youtu.be/dIwBup3d4ts>

### About arduino (C\C++) and the design:
<p> With the current state of the project the arduino code is functional but the serial comunication python script is not done yet for the current code. The main code of the previous version of the robot arm is located in 'Arduino code/robot_arm_arduino' this file was created almost a year ago, many improvements can be made and some of them are implemented in 'Arduino code/dev'.</p>
<p>The arm displayed in the last photo was built using the following main components:</p>

- 2 x Nema 23 Stepper motors
- 5 x Various sizes of Nema 17 Stepper motors
- Arduino Mega 2560
- 24V power supply
- 2 x S109 stepper motor driver 
- 5 x A4988 stepper motor driver
- 6 x hall effect sensors (Used to home each Joint)

<p> I expect to improve the design replacing the S109 stepper drivers with TB6600 drivers because of cooling issues that made them thermaly shut down during operation, replace the GT2 belts and pulleys with T5 belts (this belt profile works better with 3d printed parts), improve the wiring, etc. As electronics and hardware are not part of my current degree (Computer Science) they arer the hardest areas of the project for me.</p>

## About the Python Code.

<p> In terms of programing and maths the most complex parts of the project are solved here. Some of theese are:</p>

- Direct Kinematics: This is the mathematical process of calculating the robot's tool posicion (x,y,z,roll,pitch,yaw) based on the angles of each joint. (Code in armUtils/robotarm.py)

- Inverse Kinematics: This is the mathematical process of calculating the angles that every joint should have so that the tool of the arm reaches a certain position (x,y,z) with certian angles (roll,pitch,yaw). (Code in armUtils/robotarm.py)
- Simulation of the robot arm using openGL (arm_simulation.py), this is a keyboard controlled simulated version of the robot arm (6DOF stepper motor) shown in the previous photos. (Code in Main/arm_simulation.py). This part of the code uses the library "grafica" from <https://github.com/ivansipiran/grafica>. This is the gitHub repo used in the course "CC3501-Modelación y Computación Gráfica para Ingenieros" which is part of the study plan of "Licenciatura en Ciencias de la Ingeniería, Mención Computación v5- Universidad de Chile".    

![Simulation](\media\simulation.JPG)

<p>This simulation controlls the arm using only coordinates and euler angles of the TCP,these are then used to calculte the angles the joints should have using Inverse Kinematics. Controlls: (A,W,S,D,Q,E) are used to change x,y,z and (I,J,K,L,U,O) are used to change euler angles of the TCP </p>


