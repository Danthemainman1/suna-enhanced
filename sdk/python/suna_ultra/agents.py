"""Agent operations for Suna Ultra SDK."""

from typing import List, Optional, Dict, Any
import httpx
from .models import Agent
from .exceptions import NotFoundError, SunaError


class AgentOperations:
    """Handles agent-related operations."""
    
    def __init__(self, client: httpx.Client, base_url: str):
        """
        Initialize agent operations.
        
        Args:
            client: httpx Client instance
            base_url: Base URL for API requests
        """
        self._client = client
        self._base_url = base_url
    
    def create(
        self,
        name: str,
        type: str,
        capabilities: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> Agent:
        """
        Create a new agent.
        
        Args:
            name: Agent name
            type: Agent type (e.g., "research", "coding", "general")
            capabilities: List of agent capabilities
            config: Agent configuration
            system_prompt: System prompt for the agent
        
        Returns:
            Created Agent object
        
        Raises:
            SunaError: If creation fails
        """
        payload = {
            "name": name,
            "type": type,
        }
        
        if capabilities:
            payload["capabilities"] = capabilities
        if config:
            payload["config"] = config
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        try:
            response = self._client.post(f"{self._base_url}/agents", json=payload)
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to create agent: {e.response.text}", status_code=e.response.status_code)
    
    def get(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent object
        
        Raises:
            NotFoundError: If agent not found
            SunaError: If request fails
        """
        try:
            response = self._client.get(f"{self._base_url}/agents/{agent_id}")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to get agent: {e.response.text}", status_code=e.response.status_code)
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Agent]:
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return
            offset: Number of agents to skip
        
        Returns:
            List of Agent objects
        
        Raises:
            SunaError: If request fails
        """
        try:
            response = self._client.get(
                f"{self._base_url}/agents",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                agents_data = data
            elif isinstance(data, dict) and "agents" in data:
                agents_data = data["agents"]
            elif isinstance(data, dict) and "data" in data:
                agents_data = data["data"]
            else:
                agents_data = [data] if data else []
            
            return [Agent(**agent) for agent in agents_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list agents: {e.response.text}", status_code=e.response.status_code)
    
    def update(self, agent_id: str, **kwargs) -> Agent:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            **kwargs: Fields to update
        
        Returns:
            Updated Agent object
        
        Raises:
            NotFoundError: If agent not found
            SunaError: If update fails
        """
        try:
            response = self._client.put(f"{self._base_url}/agents/{agent_id}", json=kwargs)
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to update agent: {e.response.text}", status_code=e.response.status_code)
    
    def delete(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            True if deleted successfully
        
        Raises:
            NotFoundError: If agent not found
            SunaError: If deletion fails
        """
        try:
            response = self._client.delete(f"{self._base_url}/agents/{agent_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to delete agent: {e.response.text}", status_code=e.response.status_code)
    
    def pause(self, agent_id: str) -> Agent:
        """
        Pause an agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Updated Agent object
        
        Raises:
            NotFoundError: If agent not found
            SunaError: If pause fails
        """
        try:
            response = self._client.post(f"{self._base_url}/agents/{agent_id}/pause")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to pause agent: {e.response.text}", status_code=e.response.status_code)
    
    def resume(self, agent_id: str) -> Agent:
        """
        Resume a paused agent.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Updated Agent object
        
        Raises:
            NotFoundError: If agent not found
            SunaError: If resume fails
        """
        try:
            response = self._client.post(f"{self._base_url}/agents/{agent_id}/resume")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to resume agent: {e.response.text}", status_code=e.response.status_code)
