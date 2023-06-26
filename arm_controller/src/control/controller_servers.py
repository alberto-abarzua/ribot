import asyncio
import socket
import threading

import websockets

from utils.messages import Message
from utils.prints import console


class ControllerDependencies:
    def __init__(self, controller):
        self.controller = controller

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    @property
    def is_ready(self):
        return self.thread is not None


class WebsocketServer(ControllerDependencies):
    def __init__(self, port, controller):
        self.port = port
        self.controller = controller
        self.thread = None
        self.kill = False
        self.stop_event = threading.Event()
        self.loop = None

    async def handler(self, websocket, path):
        async for message in websocket:
            console.print(f"Received message: {message}", style="info")
            if message.strip() == "get_angles":
                angles = self.controller.get_angles()
                response = Message("0", 0, angles)
                response = response.encode()
                await websocket.send(response)
                console.print(f"Received message: {message}", style="info")

    def _start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        start_server = websockets.serve(self.handler, "0.0.0.0", self.port)
        console.print(f"Starting websocket server on port {self.port}", style="setup")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def start(self):
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread:
            self.thread.join()


class ControllerServer(ControllerDependencies):
    def __init__(self, controller, port):
        self.controller = controller
        self.port = port
        self.thread = None

        self.server_socket = None
        self.connection_socket = None

        self.connection_mutex = threading.Lock()
        self.stop_event = threading.Event()

    def _start(self):
        addr = ("0.0.0.0", 8500)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(addr)
        self.server_socket.listen(1)
        console.print(f"Listening on {addr}", style="setup")

        while not self.stop_event.is_set():
            conn, addr = self.server_socket.accept()

            console.print(f"Connected to {addr}", style="setup")
            self.connection_socket = conn
            # set timeout to None
            self.connection_socket.settimeout(None)

            self.handle_controller_connection()

    def start(self):
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()

    def _send_message(self, message):
        if not self.is_ready:
            return None
        try:
            self.connection_socket.send(message.encode())
        except OSError as e:
            console.print(f"Connection failed with error: {str(e)}", style="error")
            return None

    def send_message(self, message, mutex=False):
        if mutex:
            with self.connection_mutex:
                self._send_message(message)
        else:
            self._send_message(message)

    def _receive_message(self):
        if not self.is_ready:
            return None
        try:
            data = self.connection_socket.recv(1024)
            message = Message.decode(data)
            return message
        except OSError as e:
            console.print(f"Connection failed with error: {str(e)}", style="error")
            return None

    def receive_message(self, mutex=False):
        if mutex:
            with self.connection_mutex:
                return self._receive_message()
        else:
            return self._receive_message()

    def handle_controller_connection(self):
        while not self.stop_event.is_set():
            with self.connection_mutex:
                msg = self.receive_message()
                if msg is None:
                    break

            op = msg.op.decode()
            handler = self.controller.message_op_handlers[op]
            handler(msg)

    @property
    def is_ready(self):
        super_is_ready = super().is_ready
        return super_is_ready and self.connection_socket is not None
