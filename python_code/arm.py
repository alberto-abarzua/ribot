import sys,argparse,numpy as np
from arm_control.controller import Controller
import argparse
import platform

__author__ = "Alberto Abarzua"

DEFAULT_BAUDRATE = 115200


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parameters to run robot arm')
    parser.add_argument("--no_simulation","-n",dest = "no_simulation",action="store_false",help = "Used to run the program without the simulation.")
    parser.add_argument("--port","-p",type = str,dest = "port",help = "Selects the port to control arm if arduino is conected.")
    parser.add_argument("--baudrate","-b",type = int,dest = "baud_rate",default=DEFAULT_BAUDRATE,help = "Selects the port to control arm if arduino is conected.")
    
    args = parser.parse_args()
    port = args.port
    baudrate = args.baud_rate
    no_sim = args.no_simulation
    mac_os = True
    #Platform check
    if platform.system() == "Windows":
        mac_os = False
    if(port == None):
        baudrate = None


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
    robot_controller.cps = 60
    robot_controller.host = "127.0.0.1"
    robot_controller.port = 65433
    robot_controller.control_speed_multiplier = 1.0
    #Start the robot arm.
    robot_controller.start(simulation=no_sim,mac_os = mac_os)