"""Task operations for Suna Ultra SDK."""

import time
from typing import List, Optional, Dict, Any, Iterator
import httpx
from .models import Task, TaskResult, TaskEvent
from .exceptions import NotFoundError, SunaError, TimeoutError
from .streaming import StreamHandler


class TaskOperations:
    """Handles task-related operations."""
    
    def __init__(self, client: httpx.Client, base_url: str):
        """
        Initialize task operations.
        
        Args:
            client: httpx Client instance
            base_url: Base URL for API requests
        """
        self._client = client
        self._base_url = base_url
    
    def submit(
        self,
        agent_id: str,
        description: str,
        priority: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """
        Submit a task to an agent.
        
        Args:
            agent_id: ID of the agent to execute the task
            description: Task description
            priority: Task priority (1-10, default 5)
            context: Additional context for the task
        
        Returns:
            Created Task object
        
        Raises:
            SunaError: If submission fails
        """
        payload = {
            "agent_id": agent_id,
            "description": description,
            "priority": priority,
        }
        
        if context:
            payload["context"] = context
        
        try:
            response = self._client.post(f"{self._base_url}/tasks", json=payload)
            response.raise_for_status()
            return Task(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to submit task: {e.response.text}", status_code=e.response.status_code)
    
    def get(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task object
        
        Raises:
            NotFoundError: If task not found
            SunaError: If request fails
        """
        try:
            response = self._client.get(f"{self._base_url}/tasks/{task_id}")
            response.raise_for_status()
            return Task(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to get task: {e.response.text}", status_code=e.response.status_code)
    
    def list(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Task]:
        """
        List tasks.
        
        Args:
            agent_id: Filter by agent ID
            status: Filter by status (e.g., "pending", "running", "completed")
            limit: Maximum number of tasks to return
        
        Returns:
            List of Task objects
        
        Raises:
            SunaError: If request fails
        """
        params = {"limit": limit}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        
        try:
            response = self._client.get(f"{self._base_url}/tasks", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                tasks_data = data
            elif isinstance(data, dict) and "tasks" in data:
                tasks_data = data["tasks"]
            elif isinstance(data, dict) and "data" in data:
                tasks_data = data["data"]
            else:
                tasks_data = [data] if data else []
            
            return [Task(**task) for task in tasks_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list tasks: {e.response.text}", status_code=e.response.status_code)
    
    def cancel(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if cancelled successfully
        
        Raises:
            NotFoundError: If task not found
            SunaError: If cancellation fails
        """
        try:
            response = self._client.post(f"{self._base_url}/tasks/{task_id}/cancel")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to cancel task: {e.response.text}", status_code=e.response.status_code)
    
    def wait(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 2,
    ) -> TaskResult:
        """
        Wait for a task to complete.
        
        Args:
            task_id: Task ID
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
        
        Returns:
            TaskResult object
        
        Raises:
            TimeoutError: If task doesn't complete within timeout
            NotFoundError: If task not found
            SunaError: If polling fails
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                task = self.get(task_id)
                
                if task.status in ["completed", "failed", "cancelled"]:
                    # Get the task result
                    response = self._client.get(f"{self._base_url}/tasks/{task_id}/result")
                    response.raise_for_status()
                    return TaskResult(**response.json())
                
                time.sleep(poll_interval)
            except NotFoundError:
                raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise NotFoundError(f"Task {task_id} not found")
                # Continue polling on other errors
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    def stream(self, task_id: str) -> Iterator[TaskEvent]:
        """
        Stream task events in real-time (synchronous).
        
        Args:
            task_id: Task ID
        
        Yields:
            TaskEvent objects
        
        Raises:
            NotFoundError: If task not found
            SunaError: If streaming fails
        """
        try:
            with self._client.stream("GET", f"{self._base_url}/tasks/{task_id}/stream") as response:
                response.raise_for_status()
                yield from StreamHandler.stream_events(response)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Task {task_id} not found")
            raise SunaError(f"Failed to stream task: {e.response.text}", status_code=e.response.status_code)
