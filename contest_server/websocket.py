from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, team: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[team] = websocket

    def disconnect(self, team: str):
        if team in self.connections:
            del self.connections[team]

    async def send_message(self, team: str, message: str):
        if team in self.connections:
            await self.connections[team].send_text(message)

    async def broadcast(self, message: str):
        for ws in self.connections.values():
            await ws.send_text(message)

ws_manager = WebSocketManager()
