import sys
import numpy as np
from arm_control.controller import Controller
if __name__ == "__main__":
    port = None
    baudrate = None
    if (len(sys.argv)>1 ):
        port = sys.argv[1]
        baudrate = 115200
        assert "COM" in port or "com" in port, "Enter a valid port"


    #Create a new controller (robot arm)

    robot_controller = Controller(port = port,baudrate=baudrate)


    #set the physical parameters and constraints.

    robot_controller.robot.a2x = 0
    robot_controller.robot.a2z = 172.48
    robot_controller.robot.a3z = 173.5
    robot_controller.robot.a4z = 0

    robot_controller.robot.a4x = 126.2
    robot_controller.robot.a5x = 64.1
    robot_controller.robot.a6x = 169

    #physical constraints
    
    robot_controller.robot.j1_range = lambda x: x>-np.pi/2 and x<np.pi/2
    robot_controller.robot.j2_range = lambda x: x>-1.39626 and x<1.57
    robot_controller.robot.j3_range = lambda x: x>-np.pi/2 and x<np.pi/2
    robot_controller.robot.j5_range = lambda x: x>-np.pi/2 and x<np.pi/2

    #Accurracy of the angles sent to the arduino.
    robot_controller.acc = 10000
    #Start the robot arm.
    robot_controller.run(simulation="nosim" not in sys.argv)