"""WebSocket Manager for real-time chat."""
from typing import Dict
from fastapi import WebSocket


class WebSocketManager:
    """Manages WebSocket connections for the chat application."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """Accept and track a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: dict, exclude: str | None = None):
        """Broadcast a message to all connected clients."""
        for client_id, websocket in self.active_connections.items():
            if client_id != exclude:
                try:
                    await websocket.send_json(message)
                except Exception:
                    # Handle disconnection gracefully
                    self.disconnect(client_id)
