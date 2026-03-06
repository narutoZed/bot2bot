"""Tests for main.py"""
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


def test_root(client):
    """Test root endpoint returns message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_root_message_content(client):
    """Test root endpoint returns correct message content."""
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert "OpenCLAW Bot Chat API" in data["message"]


def test_get_agents(client):
    """Test get agents endpoint."""
    with patch("openclaw_client.OpenCLAWClient.get_agents", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [{"id": "agent1", "name": "Agent 1"}]
        response = client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()


def test_get_agents_returns_list(client):
    """Test get_agents returns a list even if empty."""
    with patch("openclaw_client.OpenCLAWClient.get_agents", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        response = client.get("/api/agents")
        
    assert response.status_code == 200
    assert response.json()["agents"] == []


def test_chat(client):
    """Test chat endpoint."""
    with patch("openclaw_client.OpenCLAWClient.send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"status": "ok", "response": "Hello"}
        response = client.post("/api/chat", json={"message": "hello", "agent_id": "agent1"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_with_default_agent(client):
    """Test chat works with default agent when agent_id not specified."""
    with patch("openclaw_client.OpenCLAWClient.send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"status": "ok", "response": "response"}
        
        response = client.post("/api/chat", json={"message": "hello"})
        
    assert response.status_code == 200
    # Should call with default agent
    mock_send.assert_called_once()
