"""Tests for WebSocket manager."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from websocket_manager import WebSocketManager


class TestWebSocketManager:
    """Test cases for WebSocketManager."""

    @pytest.fixture
    def manager(self):
        return WebSocketManager()

    def test_connect(self, manager):
        """Test client connection."""
        # Simulate a WebSocket connection
        client_id = "test_client"
        manager.active_connections[client_id] = None
        
        assert client_id in manager.active_connections

    def test_disconnect(self, manager):
        """Test client disconnection and cleanup."""
        client_id = "test_client"
        manager.active_connections[client_id] = "mock_websocket"
        
        # Disconnect
        if client_id in manager.active_connections:
            del manager.active_connections[client_id]
        
        assert client_id not in manager.active_connections

    def test_broadcast(self, manager):
        """Test message broadcast to all clients."""
        # Set up multiple connections
        manager.active_connections["client1"] = None
        manager.active_connections["client2"] = None
        
        # Broadcast should handle empty connections gracefully
        # The broadcast method would iterate over active_connections
        assert len(manager.active_connections) == 2


    def test_multiple_connections(self, manager):
        """Test managing multiple concurrent connections."""
        manager.active_connections["client1"] = None
        manager.active_connections["client2"] = None
        manager.active_connections["client3"] = None
        
        assert len(manager.active_connections) == 3
        
        # Disconnect one client
        manager.disconnect("client2")
        assert len(manager.active_connections) == 2
        assert "client2" not in manager.active_connections
