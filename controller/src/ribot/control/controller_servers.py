from __future__ import annotations

import asyncio
import socket
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Union

import websockets

from ribot.utils.fifo_lock import FIFOLock
from ribot.utils.general import no_self_call
from ribot.utils.messages import Message, MessageOp
from ribot.utils.prints import console


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


# -----------------
# ControllerServer
# -----------------


class ControllerServer(ControllerDependencies):
    class ReceiveStatusCode(Enum):
        NO_NEW_DATA = 0
        ERROR = 2
        NOT_READY = 3

    def __init__(self, controller: Any, port: int) -> None:
        super().__init__(controller)
        self.port: int = port
        self.thread: Optional[threading.Thread] = None

        self.server_socket: Optional[socket.socket] = None
        self.connection_socket: Optional[socket.socket] = None

        self._connection_mutex: FIFOLock = FIFOLock()
        self.stop_event = controller.stop_event

        self.status_time_interval: float = 1 / 30  # 30 Hz

    @property
    def connection_mutex(self) -> FIFOLock:
        return self._connection_mutex

    def status_tread_target(self) -> None:
        while not self.stop_event.is_set():
            message = Message(MessageOp.STATUS, 0)
            self.send_message(message, mutex=True)
            self.stop_event.wait(self.status_time_interval)

    def _start(self) -> None:
        addr = ("0.0.0.0", self.port)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        try:
            self.server_socket.bind(addr)
        except OSError as e:
            console.log(f"Failed to bind to address (ControllerServer) {addr} with error: {str(e)}", style="error")
            self.controller.stop()
            return

        self.server_socket.listen(1)

        console.log(f"Listening on {addr}", style="setup")

        conn, addr = self.server_socket.accept()

        self.server_socket.close()

        console.log(f"Connected to {addr}... closing server socket", style="setup")

        self.connection_socket = conn

        self.controller.set_status_running()

        self.connection_socket.setblocking(False)
        self.connection_socket.settimeout(0)

        self.controller.configure()
        self.controller.connected = True

        self.handle_controller_connection()

    def start(self) -> None:
        self.thread = threading.Thread(target=self._start)
        self.status_thread = threading.Thread(target=self.status_tread_target)

        self.thread.daemon = True
        self.thread.start()

        self.status_thread.daemon = True
        self.status_thread.start()

    @no_self_call
    def stop(self) -> None:
        console.log("Stopping controller server", style="light_info")
        if self.status_thread and self.status_thread.is_alive():
            self.status_thread.join()

        console.log("Status thread stopped", style="setup")

        if self.thread is not threading.current_thread():
            if self.thread and self.thread.is_alive():
                self.thread.join()
        console.log("Controller server stopped", style="setup")

    def _send_message(self, message: Message) -> None:
        if self.is_ready and self.connection_socket is not None:
            try:
                self.connection_socket.send(message.encode())

            except OSError as e:
                console.log(f"Connection failed with error: {str(e)}", style="error")
                self.controller.stop()

    def send_message(self, message: Message, mutex: bool = False) -> None:
        if mutex:
            with self.connection_mutex:
                self._send_message(message)
        else:
            self._send_message(message)

    def _receive_message(self, timeout: Optional[int] = None) -> Union[ControllerServer.ReceiveStatusCode, Message]:
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
            console.log(f"Connection failed with error: {str(e)}", style="error")
            self.controller.stop()
            return self.ReceiveStatusCode.ERROR

    def receive_message(
        self, mutex: bool = False, timeout: Optional[int] = None
    ) -> Union[ControllerServer.ReceiveStatusCode, Message]:
        if mutex:
            with self.connection_mutex:
                return self._receive_message(timeout=timeout)
        else:
            return self._receive_message(timeout=timeout)

    @property
    def is_ready(self) -> bool:
        super_is_ready = super().is_ready
        return super_is_ready and self.connection_socket is not None

    def handle_controller_connection(self) -> None:
        # Main loop
        while True:
            self.controller.check_last_status()
            if self.controller.stop_event.is_set():
                break

            with self.connection_mutex:
                msg = self.receive_message()

            if isinstance(msg, Message):
                handler = self.controller.message_op_handlers[msg.op]
                handler(msg)


# -----------------
# WebsocketServer
# -----------------


class WebsocketServer(ControllerDependencies):
    def __init__(self, controller: Any, port: int) -> None:
        super().__init__(controller)
        self.port: int = port

        self.stop_event = controller.stop_event

        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.server: Optional[asyncio.AbstractServer] = None

    async def handler(self, websocket: Any, _: str) -> None:
        async for message in websocket:
            if message.strip() == "get_angles":
                angles = self.controller.current_angles
                response = Message(MessageOp.STATUS, 0, angles)
                await websocket.send(response.encode())

    def _start(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            start_server = websockets.serve(  # type: ignore
                self.handler, "0.0.0.0", self.port
            )  # type: ignore
        except OSError as e:
            console.log(f"Failed to bind to address (WebsocketServer) {self.port} with error: {str(e)}", style="error")
            self.controller.stop()
            return
        console.log(f"Starting websocket server on port {self.port}", style="setup")
        self.server = asyncio.get_event_loop().run_until_complete(start_server)  # type: ignore

        asyncio.get_event_loop().run_forever()

    def start(self) -> None:
        self.thread = threading.Thread(target=self._start)
        self.thread.daemon = True
        self.thread.start()

    @no_self_call
    def stop(self) -> None:
        if self.server is not None:
            self.server.close()

        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.loop.stop)

        if self.thread is not threading.current_thread():
            if self.thread and self.thread.is_alive():
                self.thread.join()

        console.log("Websocket server stopped", style="setup")
