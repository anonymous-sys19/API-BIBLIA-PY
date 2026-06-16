import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.channels: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, ws: WebSocket):
        await ws.accept()
        if channel not in self.channels:
            self.channels[channel] = []
        self.channels[channel].append(ws)
        logger.info(f"WebSocket conectado al canal '{channel}' — total: {len(self.channels[channel])}")

    def disconnect(self, channel: str, ws: WebSocket):
        if channel in self.channels:
            self.channels[channel].remove(ws)
            if not self.channels[channel]:
                del self.channels[channel]
        logger.info(f"WebSocket desconectado del canal '{channel}'")

    async def broadcast(self, channel: str, message: dict):
        if channel not in self.channels:
            return
        disconnected = []
        for ws in self.channels[channel]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.channels[channel].remove(ws)
