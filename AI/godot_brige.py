import asyncio
import websockets

class GodotBridge:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                pass  # Можно обработать входящие сообщения от Godot, если нужно
        finally:
            self.clients.remove(websocket)

    async def send_message(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    def start(self):
        return websockets.serve(self.handler, self.host, self.port)
