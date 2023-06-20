import asyncio
import websockets
import struct

def gen_message(angles):
    print(f"Generating message for angles: {angles}")
    # pack little endian

    packed_message = struct.pack('<bii'+'f'*len(angles), 0, 0, len(angles), *angles)
    print(f"Packed message: {packed_message}")
    return packed_message

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        print(message.__repr__())
        if message.strip() == "get_angles":
            angles = [0, 0, 0.785, 0, 0, 0]
            response = gen_message(angles)
            await websocket.send(response)
            print(f"Sent response: {response}")

start_server = websockets.serve(echo, "localhost", 65433)

print("Starting server...")
asyncio.get_event_loop().run_until_complete(start_server)
print("Server started. Now running forever...")
asyncio.get_event_loop().run_forever()
