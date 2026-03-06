"""OpenCLAW Bot Chat Backend"""
from fastapi import FastAPI

app = FastAPI(title="OpenCLAW Bot Chat")


@app.get("/")
def root():
    return {"message": "OpenCLAW Bot Chat API"}


@app.get("/api/agents")
def get_agents():
    """Get list of agents from OpenCLAW Gateway"""
    return {"agents": []}


@app.post("/api/chat")
def chat(message: dict):
    """Send message to an agent"""
    return {"status": "ok"}
