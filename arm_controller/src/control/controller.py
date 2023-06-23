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
        self.connection_mutex = threading.Lock()
        self.status_rate = 0.1  # seconds

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
        self.setup_status_server()

    def _send_message(self, message):
        if self.robot_conection_socket is not None:
                    self.robot_conection_socket.send(message.encode())

    def send_message(self, message, mutex=True):
        if mutex:
            with self.connection_mutex:
                self._send_message(message)
        else:
            self._send_message(message)

    def _recieve_message(self):
        if self.robot_conection_socket is not None:
            data = self.robot_conection_socket.recv(1024)
            message = Message.decode(data)
            console.print(f"Received message: {message}", style="info")
            return message

    def receive_message(self, mutex=True):
        if mutex:
            with self.connection_mutex:
                return self._recieve_message()
        else:
            return self._recieve_message()

    def handle_controller_connection(self, conn):
        self.robot_conection_socket = conn
        # send test messge

        self.set_angles([0.5 for _ in range(6)])
        message = Message("M", 1, self.get_angles())
        console.print(f"Sending message: {message}", style="info")
        conn.send(message.encode())
        while True:
            message = Message("S", 0)
            self.send_message(message)
            resonse_message = self.receive_message()

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

    def _setup_status_server(self):
        while True:
            time.sleep(self.status_rate)
            with self.connection_mutex:
                message = Message("S", 0)
                self.send_message(message,mutex=False)
                resonse_message = self.receive_message(mutex=False)
                self.set_angles(resonse_message.args)

    def setup_status_server(self):
        thread = threading.Thread(target=self._setup_status_server)
        console.print("Starting status server", style="setup")
        thread.start()


    def setup_controller_server_socket(self):

        thread = threading.Thread(target=self._setup_controller_server_socket)
        console.print("Starting controller server socket", style="setup")
        thread.start()