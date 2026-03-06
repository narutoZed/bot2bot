"""OpenCLAW Bot Chat Backend"""
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


@app.get("/api/agents")
async def get_agents():
    """Get list of agents from OpenCLAW Gateway."""
    try:
        agents = await openclaw_client.get_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Send message to an agent."""
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    agent_id = request.agent_id or "default"
    try:
        result = await openclaw_client.send_message(agent_id, request.message)
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
            await ws_manager.broadcast({
                "client_id": client_id,
                "message": data
            }, exclude=client_id)
    except Exception:
        ws_manager.disconnect(client_id)
