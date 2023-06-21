import threading

from utils.websocket import WebsocketServer
from utils.prints import console
import socket
from utils.messages import Message
import random
import time
class ArmController:
    def __init__(self):
        self.current_angles = [0, 0, 0.5, 0, 0, 0]
        self.current_angles_lock = threading.Lock()

        self.websocket_server = WebsocketServer(65433, self)
        self.controller_socket = None 
        self.robot_conection_socket = None 

    def get_angles(self):
        with self.current_angles_lock:
            return self.current_angles

    def set_angles(self, angles):
        with self.current_angles_lock:
            self.current_angles = angles
        console.print(f"New angles: {self.current_angles}", style="info")

    def run(self):
        self.websocket_server.start()
        self.setup_controller_server_socket()




    def handle_controller_connection(self, conn):
        self.robot_conection_socket = conn
        # send test messge
        while True:
            time.sleep(1)
            random_floats = [random.random() for _ in range(6)]
            message = Message("0", 0, random_floats)
            console.print(f"Sending message: {message}", style="info")
            conn.send(message.encode())       

    def _setup_controller_server_socket(self):
        addr = ("0.0.0.0", 8500)
        self.controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.controller_socket.bind(addr)
        self.controller_socket.listen(1)
        console.print(f"Listening on {addr}", style="setup")
        while True:
            conn, addr = self.controller_socket.accept()
            console.print(f"Connected to {addr}", style="setup")
            self.handle_controller_connection(conn)

    def setup_controller_server_socket(self):
        thread = threading.Thread(target=self._setup_controller_server_socket)
        thread.start()
        thread.join()