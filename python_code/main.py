import sys
import numpy as np
from arm_control.controller import Controller



if __name__ == "__main__":

    """
    Ways of running main.py

    'python main.py <port> nosim' // Runs the controller without the simulation to a real arduino conected to a port.
    'python main.py <port>'  // Runs the controller with the simulation to a real arduino conected to a port.
    'python main.py'  // Runs the simulation without an arduino. (arduino dummy)

    """
    port = None
    baudrate = None
    if (len(sys.argv)>1 ):
        port = sys.argv[1]
        baudrate = 115200


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

    robot_controller.robot.joint_ratios = [9.3,5.36,22.5,1,3.5,1] #ratios bewtween stepper and joint.

    #Accurracy of the angles sent to the arduino.
    robot_controller.acc = 10000
    robot_controller.micro_stepping = 8
    robot_controller.cps = 30
    robot_controller.host = "127.0.0.1"
    robot_controller.port = 65433
    robot_controller.control_speed_multiplier = 0.4
    #Start the robot arm.
    robot_controller.start(simulation="nosim" not in sys.argv)