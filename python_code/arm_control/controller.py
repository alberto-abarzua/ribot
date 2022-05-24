import math
from signal import signal
import stat
import subprocess
import os.path
import sys
import csv
import socket
import time
import signal
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arm_control.serial_monitor import SerialMonitor
import arm_utils.commands as com
import arm_control.robotarm as robotarm
from arm_utils.armTransforms import Angle, OutOfBoundsError
from arm_utils.armTransforms import Config
import arm_utils.armTransforms as at
from arm_utils.filemanager import CordAngleInstruction, FileManager, SleepInstruction, ToolAngleInstruction 
from arm_utils.status import *
from arm_utils.bins import *
from arm_utils.game_pad_controller import XboxController
import threading
__author__ = "Alberto Abarzua"


class Controller():
    """Controller class, has all the controlls of the robot arm.
    """

    def __init__(self, port=None, baudrate=None) -> None:
        """Controller constructor. Creates the serial conection to the arduino. If there isn't a port or
        baudrate, a DummyArduino will be used (For testing)

        Args:
            port (string, optional): COM port of the arduino. Defaults to None.
            baudrate (int, optional): BaudRate of the arduino. Defaults to None.
        """
        #Conection to unity
        self.host = None
        self.port = None

        # Conection to arduino
       

        self.robot = robotarm.RobotArm()


        self.cps = 50 # commands per second
        self.control_speed_multiplier = 1.0

        self.acc = None  # Acurray of the angles sent to the arduino.
        self.micro_stepping = None

        self.num_joints = 6

        self.arduino_angles = [0 for _ in range(self.num_joints)] # Array used to store the exact same values the arduino

        self.is_homed = False

        self.coms_lock = threading.Lock()

        self.filem = FileManager()

        self.gamepad = ArmGamePad(self)
        self.monitor = SerialMonitor(self,port,baudrate)
        self.enable_log = False
        self.log_commands = None
        self.log_angles = None
        self.prev_time_stamp = None
        self.mac_os = False


    def create_log(self):
        self.enable_log = True
        try:
            self.log_commands = open("logs/log_commands.csv","w",newline='')
            self.log_angles = open("logs/log_angles.csv","w",newline='')
        except Exception as e:
            print(e)
        
        self.writer_commands = csv.writer(self.log_commands)
        self.writer_angles = csv.writer(self.log_angles)
        self.writer_commands.writerow(["time","steps_j1","steps_j2","steps_j3","steps_j4","steps_j5","steps_j6"]) #Write the header.
        self.writer_angles.writerow(["time","angles_j1","angles_j2","angles_j3","angles_j4","angles_j5","angles_j6"]) #Write the header.


    def log(self,time_stamp,steps,angles):
        """Adds a new entry to the log dataframe.

        Args:
            time_stamp (float): timestamp in seconds
            steps (list[int]): List of steps 


        """
        if (self.prev_time_stamp == None): #Create initial time_stamp
            self.prev_time_stamp = time_stamp
            return
        time_to_write = time_stamp- self.prev_time_stamp
        self.writer_angles.writerow([time_to_write] + angles)
        
        self.writer_commands.writerow([time_to_write] + steps)
        self.prev_time_stamp = time_stamp

    def save_log(self):
        """Saves the log to a csv file.
        """
        try:
            self.log_commands.close()
            self.log_angles.close()
            self.enable_log = False
        except Exception as e:
            print(e)
            
    @property
    def tool(self):
        """Gets the angle of the robots tool

        Returns:
            int: angle of the tool servo
        """
        return self.robot.config.tool

    @tool.setter
    def tool(self,new_angle):
        """Sets the angle of the robot's tool servo

        Args:
            new_angle (int): new angle (0-180)
        """
        self.robot.config.tool = new_angle
    @property
    def angles(self):
        """Gets the current angles of the joints of the robot arm.

        Returns:
            list[Angle]: list of angles for every joint. (current.)
        """
        return self.robot.angles

    @property
    def config(self):
        return self.robot.config

    def run_file(self,file_name):
        """Selects a file to read instructions from, sets self.cur_file. Every instruction is run by the method step()

        Args:
            file_name (str): name of the file where the instructions are stored.
        """
        self.filem.run_file(file_name)

    
    

    def step(self):
        """Makes the robot arm take a current step (read a new line from self.cur_file and run it.)

        Returns:
            bool: Ture if the file has lines left, false otherwise.
        """
        instruct = self.filem.step()

        if(instruct is None):
            return False

        if(type(instruct) is CordAngleInstruction):

            config = instruct.as_config()
            angles = self.robot.inverse_kinematics(config)
            assert angles != None, f"Config that failed: cords: {config.cords} and angles: {config.euler_angles}"
            self.move_to_angle_config(angles)
        
        if(type(instruct) is ToolAngleInstruction):
            tool = instruct.value
            self.move_gripper_to(tool)
        if(type(instruct) is SleepInstruction):
            time.sleep(instruct.value)
        return True

    
    

    def update_arduino_angles(self, angles):
        """Updates the angles that represnt the current angles array in the arduino. 

        Args:
            angles (list[Angle]): list of angles that will be added to arduino_angles
        """
        for i in range(len(angles)):
            self.arduino_angles[i] += angles[i]
        self.robot.angles = self.get_arduino_angles()

    def get_arduino_angles(self):
        """Gets the current arduino angles in Angle format.

        Returns:
            list[Angles]: current angles tracked.
        """
        return [Angle(x/self.acc, "rad") for x in self.arduino_angles]

    def send_command(self, command):
        """Sends a command to the arduino. Sends the command's message to the arduino.

        Args:
            command (Command): Calls the send method on a command, (sends it's message to the arduino)
        """
        self.monitor.send_command(command)
        
        
    def move_gripper_to(self,angle):
        """Moves the gripper to a certain angle configuration

        Args:
            angle (int): integer that represents the angle configuration of the gripper
        """
        if (self.tool == round(angle)):
            return None
        c = com.GripperCommand(self,int(angle))
        if not c.is_correct():
            raise OutOfBoundsError(self.config,"Tool out of bounds.")
        self.send_command(c)
        self.tool = int(angle)
    
    def home_arm(self):
        """Homes all the joints of the arm (runs the home command)"""
        if not self.is_homed:
            print("\nHoming all joints!")
            self.send_command(com.HomeComand(self))
    
    def unity_server(self):
        """Used to send the angles of the robot arm to the unity simulation.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept() #Waits for conection
            with conn:
                while True:
                    in_data = conn.recv(1024)
                    if not in_data:
                        continue
            
                    if (struct.unpack_from("i",in_data,offset = 0)[0] == 0):
                        #send the current angles of the arm.
                        data = Message("u",1,[int(x) for x in self.arduino_angles]+[self.tool]) 
                        conn.sendall(data.encode())
                        in_data = None

    def move_to_angle_config(self, angles):
        """Makes the robot go to a certain angle configuration (this is absolute positioning).

        Args:
            angles (list[Angles]): Angles to go to.
        """
        cons = self.robot.constraints
        angles_rads = [x.rad for x in angles]
        for i,(con,elem )in enumerate(zip(cons,angles_rads)):
            if not con(elem):
                raise OutOfBoundsError(self.config,f"Joint {i} range constraint")

        cur_angles = self.get_arduino_angles()
        dif = [Angle(fin.rad-ini.rad, "rad")
               for ini, fin in zip(cur_angles, angles)]

        if (all([abs(x.rad)<1/self.acc for x in dif])): #Check, so that only usefull commands are sent.
            return None
        command = com.MoveCommand(self, dif)
        
        self.send_command(command)

    def move_to_point(self, config):
        """Makes the tcp move to cords and certain euler angles. This is a point to point movement.

        Args:
            config (Config) : Point described as a config.
        """
        next_angles = self.robot.inverse_kinematics(config)
        self.move_to_angle_config(next_angles)
        self.move_gripper_to(config.tool)
       

    def start(self,simulation,mac_os):
        """Starts the threads to run the arm,

        Args:
            simulation (bool): If true the arm simulation will be started on another thread.
        """
        game_pad_thread = threading.Thread(target = self.gamepad.run,name= "Gamepad",daemon=True) 
        game_pad_thread.start()
        signal.signal(signal.SIGINT,self.signal_handler)
        sim_server = threading.Thread(target = self.unity_server,name= "Robot Arm Simulation",daemon=True) 
        sim_server.start()
        if simulation:
            if (not mac_os):
                self.proc_sim  = subprocess.Popen(os.path.abspath("../arm_sim_app/arm_sim.exe")) #Starts the simulation.
            else:
                path = os.path.abspath("../arm_sim_app_mac.app")
                os.chmod(path,-stat.S_IREAD)
                os.chmod(path,stat.S_IXUSR )
                self.proc_sim = subprocess.Popen(path) #Starts the simulation.
        self.monitor.run()

    def end(self):
        """Terminates the unity simulation process. Other processes are deamons so they are terminated when this parent process ends.
        """
        self.proc_sim.terminate()

    def signal_handler(self,sig,frame):
        """Used to handle Ctr + c SIGINT signal, calls self.end() to properly end the progra.

        Args:
            sig (_type_): _description_
            frame (_type_): _description_
        """
        print("\nCTRL + C ... \nEnding program")
        self.end()
        sys.exit(0)



class ArmGamePad:
    """ArmGamePad, uses an XboxController to control the postion and euler angles of the arm. Moves the arm joints to their positions.
    """

    def __init__(self,controller) -> None:
        """Starts the gamepad xbox controller.

        Args:
            controller (Controller): arm controller wich will receive the positional information from the GamePad.
        """

        self.joy = XboxController()
        self.buttons =self.joy.buttons 
        self.controller = controller
        self.robot = self.controller.robot
        #steps
        self.mult = self.controller.control_speed_multiplier
        self.dir_step = 70*self.mult
        self.angle_step = 0.3*self.mult
        self.tool_step =80*self.mult
        self.cps = self.controller.cps
        self.point_list = []
        self.cooldown =0
        self.def_cooldown = 20
        self.loop = False
        
    def create_file_point_list(self):
        """Creates a curve (set of instructions) and stores them in a text file.
        """
        curve,sleep= at.gen_curve_points(self.point_list) 
        f = self.controller.filem
        n = f.get_demo_number()
        instructions = f.from_curve_to_instruct(curve,sleep)
        f.write_file(instructions, "demo{}.txt".format(n))

        self.point_list.clear()
    def run_file(self):
        """Gets input from terminal to run a file."""
        file_name = input("\nPlease enter a file name:")
        self.controller.run_file("arm_control/data/" + file_name)
    def run_last_demo(self):
        """Runs the last demo file"""
        self.controller.run_file("arm_control/data/demo{}.txt".format(self.controller.filem.get_demo_number()-1))
    def run_loop_last_demo(self):
        """Runs on a loop the last demo file"""
        self.run_last_demo()
        self.loop = True

    def run(self):
        """Starts the main looop of the controlls
        """
        t0 = time.perf_counter()
        sign = lambda x :math.copysign(1,x)
        while(True):
            t1 = time.perf_counter()
            dt = t1 - t0
            t0 = t1
            self.robot.direct_kinematics()  # We update the euler angles and xyz
            xyz,euler_angles,tool = self.robot.config.cords,self.robot.config.euler_angles,self.robot.config.tool
            #Previous state:
            x, y,z = xyz
            A, B,C = euler_angles
            tang = tool
            #CONTROLS FOR POSITIONS

            b = self.buttons
            #---y---
            if(b["LeftJoystickX"] !=0):
                y+= sign(b["LeftJoystickX"] )*self.dir_step*dt
            #---x---
            if(b["LeftJoystickY"] !=0):
                x+= sign(b["LeftJoystickY"] )*self.dir_step*dt

            #---Z Down
            if(b["LeftTrigger"] !=0):
                z-= self.dir_step*dt
            
            #---Z up
            if(b["RightTrigger"] !=0):
                z+= self.dir_step*dt
            
            angle_step_positive = Angle(self.angle_step*dt, "rad")
            angle_step_negative = Angle(-self.angle_step*dt, "rad")


            #-- A --

            if(b["LeftBumper"] !=0):
                A.add(angle_step_negative)
                A.add(angle_step_negative)
                A.add(angle_step_negative)


            if(b["RightBumper"] !=0):
                A.add(angle_step_positive)
                A.add(angle_step_positive)
                A.add(angle_step_positive)

                   
            # -- B --

            if(b["RightJoystickY"] !=0):
                if(sign(b["RightJoystickY"] )>=0):
                    B.add(angle_step_positive)
                else:
                    B.add(angle_step_negative)

             #-- C --

            if(b["RightJoystickX"] !=0):
                if(sign(b["RightJoystickX"] )>=0):
                    C.add(angle_step_positive)
                else:
                    C.add(angle_step_negative)
            if(b["Back"]!=0): #Try and home the arm
                self.controller.home_arm()
                continue
            

            #tools controls:

            if(b["LeftDPad"] != 0):
                tang+=dt*self.tool_step

            if(b["RightDPad"] != 0):
                tang-=dt*self.tool_step

            #file and point management.

            if (b["Y"] !=0): #Save a new point
                if(b["X"] !=0):
                    self.point_list.clear()
                    self.cooldown =self.def_cooldown
                    continue
                if(self.cooldown ==0):
                    self.point_list.append(Config([x, y, z], [A, B,C],round(tang)))
                    [print(x, end = " ") for x in self.point_list]
                    self.cooldown =self.def_cooldown
            
            if (b["X"] !=0): #Save file and clear point list.
                if(self.cooldown ==0):
                    self.cooldown =self.def_cooldown
                    try:
                        self.create_file_point_list()
                        print("File demo{}.txt created!".format(self.controller.filem.get_demo_number()))
                    except:
                        print("point list not valid")

            if (b["UpDPad"]!=0): #save log file
                    if(self.cooldown ==0):
                        print("saving log!")

                        self.controller.save_log()
                        self.cooldown =self.def_cooldown*3

            if (b["DownDPad"]!=0): #create log file.
                    if(self.cooldown ==0):
                        print("creating new  log!")

                        self.controller.create_log()
                        self.cooldown =self.def_cooldown*3
            if (b["A"] !=0):
                if(self.cooldown ==0):
                    self.run_last_demo()
                    self.cooldown =self.def_cooldown


            if (b["B"] !=0):
                if(self.cooldown ==0):
                    [print(x, end = " ") for x in self.point_list]
                    self.cooldown =self.def_cooldown

            if (b["Start"] !=0):
                 if(self.cooldown ==0):
                    if(self.loop == True):
                        self.loop = False
                        self.cooldown =self.def_cooldown
                        self.controller.filem.interrupt_file()
                        continue
                    self.run_loop_last_demo()
                    self.cooldown =self.def_cooldown
            try:
                if (not self.controller.step()):
                    if(self.loop):
                        self.run_last_demo()
                        continue
                    self.controller.move_to_point(Config([x, y, z], [A, B,C],round(tang)))
                assert  self.controller.coms_lock.locked() == False #Check that the controller arduino is not BUSY
            except Exception as e:
                if len(str(e))>0:
                    print(e)
                x, y,z = xyz
                A, B,C = euler_angles
                tang = tool

            if (self.cooldown>0):
                self.cooldown-=1
            time.sleep(max(0,(1/self.cps)-dt)) #adjust for the required fps
