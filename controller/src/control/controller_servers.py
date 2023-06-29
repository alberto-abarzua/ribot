import asyncio
import queue
import socket
import threading
import time

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


class FIFOLock:
    def __init__(self):
        self.internal_lock = threading.Lock()
        self.queue = queue.Queue()
        self.current_owner = None

    def acquire(self):
        current_thread = threading.get_ident()
        self.queue.put(current_thread)
        while self.queue.queue[0] != current_thread or not self.internal_lock.acquire(False):
            pass
        self.current_owner = current_thread

    def release(self):
        self.internal_lock.release()
        self.queue.get()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class WebsocketServer(ControllerDependencies):
    def __init__(self, port, controller):
        self.port = port
        self.controller = controller
        self.thread = None
        self.kill = False
        self.stop_event = threading.Event()
        self.loop = None

    async def handler(self, websocket, _):
        async for message in websocket:
            console.print(f"Received message: {message}", style="info")
            if message.strip() == "get_angles":
                angles = self.controller.current_angles
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

        self._connection_mutex = FIFOLock()

        self.status_time_interval = 1 / 30  # 30 Hz
        self.stop_event = threading.Event()

        self.last_status_time = time.time()

    @property
    def connection_mutex(self):
        return self._connection_mutex

    def _start_status(self):
        while not self.stop_event.is_set():
            message = Message("S", 0)
            self.send_message(message, mutex=True)
            self.last_status_time = time.time()
            self.stop_event.wait(self.status_time_interval)

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
            # Make the socket non-blocking
            self.connection_socket.setblocking(0)
            self.connection_socket.settimeout(0)

            self.handle_controller_connection()

    def start(self):
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

        self.status_thread = threading.Thread(target=self._start_status)
        self.status_thread.daemon = True
        self.status_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.status_thread:
            self.status_thread.join()
        if self.thread:
            self.thread.join()

    def _send_message(self, message):
        if not self.is_ready:
            return None
        try:
            op = message.op
            style = "info"
            if op != "S":
                style = "big_info"

            console.print(f"Sending message: {message}", style=style)
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

    def _receive_message(self, timeout=None):
        if not self.is_ready:
            return None
        try:
            if timeout is not None:
                self.connection_socket.settimeout(timeout)
                self.connection_socket.setblocking(1)

            header_data = self.connection_socket.recv(Message.LENGTH_HEADERS)
            if not header_data:
                return False
            _, _, num_args = Message.decode_headers(header_data)
            data = header_data
            if num_args > 0:
                body_data = self.connection_socket.recv(num_args * 4)
                if not body_data:
                    return False
                data += body_data
            if timeout is not None:
                self.connection_socket.setblocking(0)
                self.connection_socket.settimeout(0)
            if not data:
                return False
            message = Message.decode(data)
            return message
        except BlockingIOError:
            return False
        except OSError as e:
            console.print(f"Connection failed with error: {str(e)}", style="error")
            return None

    def receive_message(self, mutex=False, timeout=None):
        if mutex:
            with self.connection_mutex:
                return self._receive_message(timeout=timeout)
        else:
            return self._receive_message(timeout=timeout)

    def signal_status(self):
        diff = time.time() - self.last_status_time
        if diff > self.status_time_interval:
            self.signal_send_status.set()
            self.continue_recv_status.clear()
            self.continue_recv_status.wait()

    def handle_controller_connection(self):
        while not self.stop_event.is_set():
            with self.connection_mutex:
                msg = self.receive_message()

            data_available = not (msg is False or msg is None)
            if data_available:
                op = msg.op.decode()
                handler = self.controller.message_op_handlers[op]
                handler(msg)

    @property
    def is_ready(self):
        super_is_ready = super().is_ready
        return super_is_ready and self.connection_socket is not None
