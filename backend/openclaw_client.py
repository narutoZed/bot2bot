"""OpenCLAW Gateway API Client."""
import httpx
from typing import Any


class OpenCLAWClient:
    """Client for interacting with OpenCLAW Gateway API."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    async def get_agents(self) -> list[dict[str, Any]]:
        """Get list of agents from OpenCLAW Gateway."""
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.request(
                "GET",
                f"{self.base_url}/api/v1/agents",
                timeout=30.0,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to get agents: {response.status_code}")
            data = response.json()
            return data.get("agents", [])

    async def send_message(self, agent_id: str, message: str) -> dict[str, Any]:
        """Send message to a specific agent."""
        async with httpx.AsyncClient(trust_env=False) as client:
            response = await client.request(
                "POST",
                f"{self.base_url}/api/v1/agents/{agent_id}/messages",
                json={"content": message},
                timeout=30.0,
            )
            if response.status_code != 200:
                raise Exception(f"Failed to send message: {response.status_code}")
            return response.json()
