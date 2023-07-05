from __future__ import annotations

import asyncio
import queue
import socket
import threading
import time
import types
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Type, Union

import websockets

from utils.messages import Message
from utils.prints import console


class ControllerDependencies(ABC):
    def __init__(self, controller: Any) -> None:
        self.controller: Any = controller
        self.thread: Optional[threading.Thread] = None

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @property
    def is_ready(self) -> bool:
        return self.thread is not None


class FIFOLock:
    def __init__(self) -> None:
        self.internal_lock: threading.Lock = threading.Lock()
        self.queue: queue.Queue = queue.Queue()
        self.current_owner: Optional[int] = None

    def acquire(self) -> None:
        current_thread: int = threading.get_ident()
        self.queue.put(current_thread)
        while self.queue.queue[0] != current_thread or not self.internal_lock.acquire(False):
            pass
        self.current_owner = current_thread

    def release(self) -> None:
        self.internal_lock.release()
        self.queue.get()

    def __enter__(self) -> None:
        self.acquire()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        self.release()


class WebsocketServer(ControllerDependencies):
    def __init__(self, port: int, controller: Any) -> None:
        super().__init__(controller)
        self.port: int = port
        self.kill: bool = False
        self.stop_event: threading.Event = threading.Event()

        self.loop: Optional[asyncio.AbstractEventLoop] = None  # asyncio event loop

    async def handler(self, websocket: Any, _: str) -> None:
        async for message in websocket:
            console.print(f"Received message: {message}", style="info")
            if message.strip() == "get_angles":
                angles = self.controller.current_angles
                response = Message("0", 0, angles)
                await websocket.send(response.encode())
                console.print(f"Received message: {message}", style="info")

    def _start(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        start_server = websockets.serve(self.handler, "0.0.0.0", self.port)  # type: ignore
        console.print(f"Starting websocket server on port {self.port}", style="setup")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def start(self) -> None:
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread is not None:
            self.thread.join()


class ControllerServer(ControllerDependencies):
    def __init__(self, controller: Any, port: int) -> None:
        super().__init__(controller)
        self.port: int = port
        self.thread: Optional[threading.Thread] = None

        self.server_socket: Optional[socket.socket] = None
        self.connection_socket: Optional[socket.socket] = None

        self._connection_mutex: FIFOLock = FIFOLock()

        self.status_time_interval: float = 1 / 30  # 30 Hz
        self.stop_event: threading.Event = threading.Event()

        self.last_status_time: float = time.time()

    @property
    def connection_mutex(self) -> FIFOLock:
        return self._connection_mutex

    def _start_status(self) -> None:
        while not self.stop_event.is_set():
            message = Message("S", 0)
            self.send_message(message, mutex=True)
            self.last_status_time = time.time()
            self.stop_event.wait(self.status_time_interval)

    def _start(self) -> None:
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
            self.connection_socket.setblocking(False)
            self.connection_socket.settimeout(0)

            self.handle_controller_connection()

    def start(self) -> None:
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

        self.status_thread = threading.Thread(target=self._start_status)
        self.status_thread.daemon = True
        self.status_thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.status_thread:
            self.status_thread.join()
        if self.thread:
            self.thread.join()

    def _send_message(self, message: Message) -> None:
        if self.is_ready and self.connection_socket is not None:
            try:
                op = message.op
                style = "info"
                if op != "S":
                    style = "big_info"

                console.print(f"Sending message: {message}", style=style)
                self.connection_socket.send(message.encode())
            except OSError as e:
                console.print(f"Connection failed with error: {str(e)}", style="error")

    def send_message(self, message: Message, mutex: bool = False) -> None:
        if mutex:
            with self.connection_mutex:
                self._send_message(message)
        else:
            self._send_message(message)

    class ReceiveStatusCode(Enum):
        NO_NEW_DATA = 0
        ERROR = 2
        NOT_READY = 3

    def _receive_message(
        self, timeout: Optional[int] = None
    ) -> Union[ControllerServer.ReceiveStatusCode, Message]:
        if not self.is_ready or self.connection_socket is None:
            return self.ReceiveStatusCode.NOT_READY
        try:
            if timeout is not None:
                self.connection_socket.settimeout(timeout)
                self.connection_socket.setblocking(True)

            header_data = self.connection_socket.recv(Message.LENGTH_HEADERS)
            if not header_data:
                return self.ReceiveStatusCode.NO_NEW_DATA
            _, _, num_args = Message.decode_headers(header_data)
            data = header_data
            if num_args > 0:
                body_data = self.connection_socket.recv(num_args * 4)
                if not body_data:
                    return self.ReceiveStatusCode.NO_NEW_DATA
                data += body_data
            if timeout is not None:
                self.connection_socket.setblocking(False)
                self.connection_socket.settimeout(0)
            if not data:
                return self.ReceiveStatusCode.NO_NEW_DATA
            message = Message.decode(data)
            return message
        except BlockingIOError:
            return self.ReceiveStatusCode.NO_NEW_DATA
        except OSError as e:
            console.print(f"Connection failed with error: {str(e)}", style="error")
            return self.ReceiveStatusCode.ERROR

    def receive_message(
        self, mutex: bool = False, timeout: Optional[int] = None
    ) -> Union[ControllerServer.ReceiveStatusCode, Message]:
        if mutex:
            with self.connection_mutex:
                return self._receive_message(timeout=timeout)
        else:
            return self._receive_message(timeout=timeout)

    def handle_controller_connection(self) -> None:
        while not self.stop_event.is_set():
            with self.connection_mutex:
                msg = self.receive_message()

            if isinstance(msg, Message):
                handler = self.controller.message_op_handlers[msg.op]
                handler(msg)

    @property
    def is_ready(self) -> bool:
        super_is_ready = super().is_ready
        return super_is_ready and self.connection_socket is not None
