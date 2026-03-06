"""Tests for API routes."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_agents(client):
    """Test GET /api/agents returns agent list."""
    with patch("openclaw_client.OpenCLAWClient.get_agents", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [
            {"id": "agent1", "name": "Agent 1"},
            {"id": "agent2", "name": "Agent 2"},
        ]
        
        response = client.get("/api/agents")
        
    assert response.status_code == 200
    assert "agents" in response.json()
    assert len(response.json()["agents"]) == 2


def test_get_agents_gateway_unavailable(client):
    """Test GET /api/agents returns 503 when Gateway unavailable."""
    with patch("openclaw_client.OpenCLAWClient.get_agents", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("Gateway unavailable")
        
        response = client.get("/api/agents")
        
    assert response.status_code == 503


def test_post_chat(client):
    """Test POST /api/chat sends message."""
    with patch("openclaw_client.OpenCLAWClient.send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"status": "ok", "response": "Hello"}
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "agent_id": "agent1"
        })
        
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_post_chat_missing_content(client):
    """Test POST /api/chat returns 422 when message is missing (Pydantic validation)."""
    response = client.post("/api/chat", json={})
    
    # FastAPI returns 422 for validation errors by default
    assert response.status_code == 422


def test_post_chat_agent_not_found(client):
    """Test POST /api/chat returns 404 when agent not found."""
    with patch("openclaw_client.OpenCLAWClient.send_message", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("Agent not found: invalid_agent")
        
        response = client.post("/api/chat", json={
            "message": "Hello",
            "agent_id": "invalid_agent"
        })
        
    assert response.status_code == 404
