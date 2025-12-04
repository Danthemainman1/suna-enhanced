"""Synchronous client for Suna Ultra SDK."""

from typing import Optional
import httpx
from .auth import Auth
from .agents import AgentOperations
from .tasks import TaskOperations
from .workflows import WorkflowOperations
from .tools import ToolOperations
from .exceptions import SunaError


class SunaClient:
    """
    Synchronous client for the Suna Ultra API.
    
    Usage:
        >>> from suna_ultra import SunaClient
        >>> 
        >>> client = SunaClient(api_key="sk-...")
        >>> 
        >>> # Create an agent
        >>> agent = client.agents.create(name="Research Agent", type="research")
        >>> 
        >>> # Submit a task
        >>> task = client.tasks.submit(agent.agent_id, "Research AI trends")
        >>> 
        >>> # Wait for completion
        >>> result = client.tasks.wait(task.id, timeout=300)
        >>> print(result.output)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
    ):
        """
        Initialize the Suna Ultra client.
        
        Args:
            api_key: API key for authentication. If not provided, will try SUNA_API_KEY env var.
            base_url: Base URL of the Suna Ultra API
            timeout: Default timeout for requests in seconds
        
        Raises:
            AuthenticationError: If no API key is provided or found
        """
        self._auth = Auth(api_key)
        self._base_url = base_url.rstrip("/") + "/api"
        self._timeout = timeout
        
        # Create HTTP client with auth headers
        self._client = httpx.Client(
            headers=self._auth.get_headers(),
            timeout=timeout,
        )
        
        # Initialize operation handlers
        self._agents = AgentOperations(self._client, self._base_url)
        self._tasks = TaskOperations(self._client, self._base_url)
        self._workflows = WorkflowOperations(self._client, self._base_url)
        self._tools = ToolOperations(self._client, self._base_url)
    
    @property
    def agents(self) -> AgentOperations:
        """Access agent operations."""
        return self._agents
    
    @property
    def tasks(self) -> TaskOperations:
        """Access task operations."""
        return self._tasks
    
    @property
    def workflows(self) -> WorkflowOperations:
        """Access workflow operations."""
        return self._workflows
    
    @property
    def tools(self) -> ToolOperations:
        """Access tool operations."""
        return self._tools
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
