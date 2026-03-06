"""Tests for main.py"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


def test_get_agents(client):
    """Test get agents endpoint."""
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()


def test_chat(client):
    """Test chat endpoint."""
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
