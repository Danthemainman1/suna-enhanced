"""Asynchronous client for Suna Ultra SDK."""

import time
from typing import Optional, AsyncIterator, List, Dict, Any
import httpx
from .auth import Auth
from .models import Agent, Task, TaskResult, TaskEvent, Workflow, WorkflowRun, Tool, ToolResult
from .exceptions import SunaError, NotFoundError, TimeoutError
from .streaming import StreamHandler


class AsyncAgentOperations:
    """Async agent operations."""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url
    
    async def create(self, name: str, type: str, capabilities: Optional[List[str]] = None, 
                    config: Optional[Dict[str, Any]] = None, system_prompt: Optional[str] = None) -> Agent:
        payload = {"name": name, "type": type}
        if capabilities:
            payload["capabilities"] = capabilities
        if config:
            payload["config"] = config
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        try:
            response = await self._client.post(f"{self._base_url}/agents", json=payload)
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to create agent: {e.response.text}", status_code=e.response.status_code)
    
    async def get(self, agent_id: str) -> Agent:
        try:
            response = await self._client.get(f"{self._base_url}/agents/{agent_id}")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to get agent: {e.response.text}", status_code=e.response.status_code)
    
    async def list(self, limit: int = 100, offset: int = 0) -> List[Agent]:
        try:
            response = await self._client.get(f"{self._base_url}/agents", params={"limit": limit, "offset": offset})
            response.raise_for_status()
            data = response.json()
            agents_data = data if isinstance(data, list) else data.get("agents", data.get("data", []))
            return [Agent(**agent) for agent in agents_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list agents: {e.response.text}", status_code=e.response.status_code)
    
    async def update(self, agent_id: str, **kwargs) -> Agent:
        try:
            response = await self._client.put(f"{self._base_url}/agents/{agent_id}", json=kwargs)
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to update agent: {e.response.text}", status_code=e.response.status_code)
    
    async def delete(self, agent_id: str) -> bool:
        try:
            response = await self._client.delete(f"{self._base_url}/agents/{agent_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to delete agent: {e.response.text}", status_code=e.response.status_code)
    
    async def pause(self, agent_id: str) -> Agent:
        try:
            response = await self._client.post(f"{self._base_url}/agents/{agent_id}/pause")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to pause agent: {e.response.text}", status_code=e.response.status_code)
    
    async def resume(self, agent_id: str) -> Agent:
        try:
            response = await self._client.post(f"{self._base_url}/agents/{agent_id}/resume")
            response.raise_for_status()
            return Agent(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Agent {agent_id} not found")
            raise SunaError(f"Failed to resume agent: {e.response.text}", status_code=e.response.status_code)


class AsyncTaskOperations:
    """Async task operations."""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url
    
    async def submit(self, agent_id: str, description: str, priority: int = 5, 
                    context: Optional[Dict[str, Any]] = None) -> Task:
        payload = {"agent_id": agent_id, "description": description, "priority": priority}
        if context:
            payload["context"] = context
        
        try:
            response = await self._client.post(f"{self._base_url}/tasks", json=payload)
            response.raise_for_status()
            return Task(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to submit task: {e.response.text}", status_code=e.response.status_code)
    
    async def get(self, task_id: str) -> Task:
        try:
            response = await self._client.get(f"{self._base_url}/tasks/{task_id}")
            response.raise_for_status()
            return Task(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to get task: {e.response.text}", status_code=e.response.status_code)
    
    async def list(self, agent_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[Task]:
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        
        try:
            response = await self._client.get(f"{self._base_url}/tasks", params=params)
            response.raise_for_status()
            data = response.json()
            tasks_data = data if isinstance(data, list) else data.get("tasks", data.get("data", []))
            return [Task(**task) for task in tasks_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list tasks: {e.response.text}", status_code=e.response.status_code)
    
    async def cancel(self, task_id: str) -> bool:
        try:
            response = await self._client.post(f"{self._base_url}/tasks/{task_id}/cancel")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to cancel task: {e.response.text}", status_code=e.response.status_code)
    
    async def wait(self, task_id: str, timeout: int = 300, poll_interval: int = 2) -> TaskResult:
        import asyncio
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                task = await self.get(task_id)
                if task.status in ["completed", "failed", "cancelled"]:
                    response = await self._client.get(f"{self._base_url}/tasks/{task_id}/result")
                    response.raise_for_status()
                    return TaskResult(**response.json())
                await asyncio.sleep(poll_interval)
            except NotFoundError:
                raise
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    async def stream(self, task_id: str) -> AsyncIterator[TaskEvent]:
        try:
            async with self._client.stream("GET", f"{self._base_url}/tasks/{task_id}/stream") as response:
                response.raise_for_status()
                async for event in StreamHandler.stream_events_async(response):
                    yield event
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to stream task: {e.response.text}", status_code=e.response.status_code)


class AsyncWorkflowOperations:
    """Async workflow operations."""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url
    
    async def create(self, name: str, definition: Dict[str, Any]) -> Workflow:
        try:
            response = await self._client.post(f"{self._base_url}/workflows", json={"name": name, "definition": definition})
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to create workflow: {e.response.text}", status_code=e.response.status_code)
    
    async def get(self, workflow_id: str) -> Workflow:
        try:
            response = await self._client.get(f"{self._base_url}/workflows/{workflow_id}")
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to get workflow: {e.response.text}", status_code=e.response.status_code)
    
    async def list(self) -> List[Workflow]:
        try:
            response = await self._client.get(f"{self._base_url}/workflows")
            response.raise_for_status()
            data = response.json()
            workflows_data = data if isinstance(data, list) else data.get("workflows", data.get("data", []))
            return [Workflow(**workflow) for workflow in workflows_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list workflows: {e.response.text}", status_code=e.response.status_code)
    
    async def update(self, workflow_id: str, definition: Dict[str, Any]) -> Workflow:
        try:
            response = await self._client.put(f"{self._base_url}/workflows/{workflow_id}", json={"definition": definition})
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to update workflow: {e.response.text}", status_code=e.response.status_code)
    
    async def delete(self, workflow_id: str) -> bool:
        try:
            response = await self._client.delete(f"{self._base_url}/workflows/{workflow_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to delete workflow: {e.response.text}", status_code=e.response.status_code)
    
    async def run(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None) -> WorkflowRun:
        try:
            response = await self._client.post(f"{self._base_url}/workflows/{workflow_id}/run", json={"inputs": inputs or {}})
            response.raise_for_status()
            return WorkflowRun(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to run workflow: {e.response.text}", status_code=e.response.status_code)


class AsyncToolOperations:
    """Async tool operations."""
    
    def __init__(self, client: httpx.AsyncClient, base_url: str):
        self._client = client
        self._base_url = base_url
    
    async def list(self, category: Optional[str] = None) -> List[Tool]:
        params = {}
        if category:
            params["category"] = category
        
        try:
            response = await self._client.get(f"{self._base_url}/tools", params=params)
            response.raise_for_status()
            data = response.json()
            tools_data = data if isinstance(data, list) else data.get("tools", data.get("data", []))
            return [Tool(**tool) for tool in tools_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list tools: {e.response.text}", status_code=e.response.status_code)
    
    async def get(self, tool_name: str) -> Tool:
        try:
            response = await self._client.get(f"{self._base_url}/tools/{tool_name}")
            response.raise_for_status()
            return Tool(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Tool {tool_name} not found")
            raise SunaError(f"Failed to get tool: {e.response.text}", status_code=e.response.status_code)
    
    async def execute(self, tool_name: str, **params: Any) -> ToolResult:
        try:
            response = await self._client.post(f"{self._base_url}/tools/execute", json={"tool_name": tool_name, "parameters": params})
            response.raise_for_status()
            return ToolResult(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Tool {tool_name} not found")
            raise SunaError(f"Failed to execute tool: {e.response.text}", status_code=e.response.status_code)


class AsyncSunaClient:
    """
    Asynchronous client for the Suna Ultra API.
    
    Usage:
        >>> from suna_ultra import AsyncSunaClient
        >>> 
        >>> async with AsyncSunaClient(api_key="...") as client:
        >>>     agent = await client.agents.create(name="Agent", type="research")
        >>>     
        >>>     async for event in client.tasks.stream(task.id):
        >>>         print(event.data)
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize async Suna Ultra client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL of the Suna Ultra API
            timeout: Default timeout for requests in seconds
        """
        self._auth = Auth(api_key)
        self._base_url = base_url.rstrip("/") + "/api"
        self._timeout = timeout
        
        self._client = httpx.AsyncClient(headers=self._auth.get_headers(), timeout=timeout)
        
        self._agents = AsyncAgentOperations(self._client, self._base_url)
        self._tasks = AsyncTaskOperations(self._client, self._base_url)
        self._workflows = AsyncWorkflowOperations(self._client, self._base_url)
        self._tools = AsyncToolOperations(self._client, self._base_url)
    
    @property
    def agents(self) -> AsyncAgentOperations:
        """Access agent operations."""
        return self._agents
    
    @property
    def tasks(self) -> AsyncTaskOperations:
        """Access task operations."""
        return self._tasks
    
    @property
    def workflows(self) -> AsyncWorkflowOperations:
        """Access workflow operations."""
        return self._workflows
    
    @property
    def tools(self) -> AsyncToolOperations:
        """Access tool operations."""
        return self._tools
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
