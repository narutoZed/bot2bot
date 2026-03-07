"""OpenCLAW Bot Chat Backend"""

import subprocess
import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openclaw_client import OpenCLAWClient
from websocket_manager import WebSocketManager
from fastapi import WebSocket

app = FastAPI(title="OpenCLAW Bot Chat")
ws_manager = WebSocketManager()
openclaw_client = OpenCLAWClient()


class ChatRequest(BaseModel):
    message: str
    agent_id: str | None = None


@app.get("/")
def root():
    return {"message": "OpenCLAW Bot Chat API"}


def get_agents_from_openclaw() -> list[dict]:
    """Get agents from OpenCLAW CLI."""
    try:
        output = subprocess.check_output(
            ["openclaw", "agents", "list"], timeout=10, text=True
        )
        agents = []
        for line in output.split("\n"):
            # Match "- agentName" or "- agentName (default)" format
            match = re.match(r"^- (\w+)", line)
            if match:
                agent_id = match.group(1)
                is_default = "(default)" in line
                agents.append(
                    {
                        "id": agent_id,
                        "name": agent_id,
                        "emoji": "⭐" if is_default else "🤖",
                    }
                )
        return agents
    except Exception as e:
        print(f"[ERROR] Failed to get agents: {e}")
        return []


@app.get("/api/agents")
async def get_agents():
    """Get list of agents from OpenCLAW Gateway."""
    try:
        agents = get_agents_from_openclaw()
        if not agents:
            # Fallback to default agents
            agents = [
                {"id": "main", "name": "Main Agent", "emoji": "🤖"},
                {"id": "default", "name": "Default Agent", "emoji": "🦊"},
            ]
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Send message to an agent and broadcast response via WebSocket."""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")

    agent_id = request.agent_id or "default"
    try:
        result = await openclaw_client.send_message(agent_id, request.message)

        # Broadcast agent response to all connected clients via WebSocket
        response_content = (
            result.get("response") or result.get("message") or str(result)
        )
        await ws_manager.broadcast({"client_id": agent_id, "message": response_content})

        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time chat."""
    await ws_manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all clients
            await ws_manager.broadcast(
                {"client_id": client_id, "message": data}, exclude=client_id
            )
    except Exception:
        ws_manager.disconnect(client_id)
