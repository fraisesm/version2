from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, team: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[team] = websocket
        logger.info(f"Team {team} connected. Total connections: {len(self.connections)}")

    def disconnect(self, team: str):
        if team in self.connections:
            del self.connections[team]
            logger.info(f"Team {team} disconnected. Total connections: {len(self.connections)}")

    async def send_message(self, team: str, message: str):
        if team in self.connections:
            try:
                await self.connections[team].send_text(message)
                logger.debug(f"Message sent to team {team}: {message}")
            except Exception as e:
                logger.error(f"Error sending message to team {team}: {str(e)}")
                self.disconnect(team)

    async def broadcast(self, message: str):
        logger.info(f"Broadcasting message to {len(self.connections)} connections: {message}")
        disconnected_teams = []
        for team, ws in self.connections.items():
            try:
                await ws.send_text(message)
                logger.debug(f"Broadcast message sent to team {team}")
            except Exception as e:
                logger.error(f"Error broadcasting to team {team}: {str(e)}")
                disconnected_teams.append(team)
        
        # Удаляем отключенные соединения
        for team in disconnected_teams:
            self.disconnect(team)

ws_manager = WebSocketManager()
