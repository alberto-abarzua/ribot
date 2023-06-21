import asyncio
import threading

import websockets

from utils.messages import Message
from utils.prints import console


class WebsocketServer:
    def __init__(self, port, controller):
        self.port = port
        self.controller = controller
        self.server_thread = None

    async def handler(self, websocket, path):
        async for message in websocket:
            console.print(f"Received message: {message}", style="info")
            if message.strip() == "get_angles":
                angles = self.controller.get_angles()
                response = Message("0", 0,angles)
                response = response.encode()
                await websocket.send(response)
                console.print(f"Received message: {message}", style="info")

    def _start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, "0.0.0.0", self.port)
        console.print(f"Starting websocket server on port {self.port}", style="setup")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def start(self):
        self.server_thread = threading.Thread(target=self._start)
        self.server_thread.start()

    def stop(self):
        self.server_thread.join()
