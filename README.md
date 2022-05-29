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
![Whole view](https://i.ibb.co/3yFSxkv/16750-C46-705-C-4-CE6-94-A2-35-F1-C98-ADB11.jpg)
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

- Arm simulation: Created using unity, receives the angles from python code using a socket displaying the current configuration of the robot arm.
![Simulation](https://i.ibb.co/7bJFz8Q/img.png)

- Arm Controller: The arm controller takes charge of all the controlls and comunication to the arduino. The controller runs the controll logic with an xbox controller,
gives the inputs to the serial monitor, and runs the simulation with the current angles of the robot 


The controller can be started in a few different ways, these include:

 * Support for macOS
 * Run the program with or without the unity simulation displaying the current configuration of the arm.
 * Run the controller conected to a real arduino or without one (if no port is specified)

```
    To view information on how to run the controller, run

    'python arm.py --help'

    Requirements:

    Python 3.10

    Libraries installation are in 
    requirements.txt
```
