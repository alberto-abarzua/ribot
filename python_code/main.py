import sys
import os
from arm_control.arm_simulation import sim
from threading import Thread
from arm_control.serial_monitor import SerialMonitor
from arm_control.controller import Controller
from arm_control.game_pad_controller import ArmGamePad
if __name__ == "__main__":
    port = None
    baudrate = None
    if (len(sys.argv)>1 ):
        port = sys.argv[1]
        baudrate = 115200

        assert "COM" in port , "Enter a valid port"

    c = Controller(port = port,baudrate= baudrate)
    g = ArmGamePad(c)
    sim_thread = Thread(target = sim,args =(c,),name= "Robot Arm Simulation",daemon=True) 
    game_thread = Thread(target = g.run,name= "Gamepad",daemon=True) 

    #Run the simulation on another thread.
    sim_thread.start()
    game_thread.start()
    c.monitor.run()

#    m1 9000 0 0 0 0 0