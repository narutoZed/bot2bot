"""Tests for OpenCLAW API client."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock, patch, MagicMock
from openclaw_client import OpenCLAWClient


class TestOpenCLAWClient:
    """Test cases for OpenCLAWClient."""

    @pytest.fixture
    def client(self):
        return OpenCLAWClient(base_url="http://localhost:8080")

    @pytest.mark.asyncio
    async def test_get_agents_success(self, client):
        """Test getting agents list successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "agents": [
                {"id": "agent1", "name": "Agent 1"},
                {"id": "agent2", "name": "Agent 2"},
            ]
        }
        
        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            agents = await client.get_agents()
            
        assert len(agents) == 2
        assert agents[0]["id"] == "agent1"

    @pytest.mark.asyncio
    async def test_send_message_success(self, client):
        """Test sending message to agent successfully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "response": "Hello from agent"
        }
        
        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.send_message("agent1", "Hello")
            
        assert result["status"] == "ok"
        assert result["response"] == "Hello from agent"

    @pytest.mark.asyncio
    async def test_get_agents_timeout(self, client):
        """Test API timeout handling."""
        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = TimeoutError("Request timeout")
            
            with pytest.raises(TimeoutError):
                await client.get_agents()

    @pytest.mark.asyncio
    async def test_send_message_error_response(self, client):
        """Test API error response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Agent not found"
        
        with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(Exception, match="404"):
                await client.send_message("invalid_agent", "Hello")
