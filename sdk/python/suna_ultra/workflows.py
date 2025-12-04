"""Workflow operations for Suna Ultra SDK."""

from typing import List, Optional, Dict, Any
import httpx
from .models import Workflow, WorkflowRun
from .exceptions import NotFoundError, SunaError


class WorkflowOperations:
    """Handles workflow-related operations."""
    
    def __init__(self, client: httpx.Client, base_url: str):
        """
        Initialize workflow operations.
        
        Args:
            client: httpx Client instance
            base_url: Base URL for API requests
        """
        self._client = client
        self._base_url = base_url
    
    def create(self, name: str, definition: Dict[str, Any]) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            definition: Workflow definition (DAG structure)
        
        Returns:
            Created Workflow object
        
        Raises:
            SunaError: If creation fails
        """
        payload = {
            "name": name,
            "definition": definition,
        }
        
        try:
            response = self._client.post(f"{self._base_url}/workflows", json=payload)
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to create workflow: {e.response.text}", status_code=e.response.status_code)
    
    def get(self, workflow_id: str) -> Workflow:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow object
        
        Raises:
            NotFoundError: If workflow not found
            SunaError: If request fails
        """
        try:
            response = self._client.get(f"{self._base_url}/workflows/{workflow_id}")
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to get workflow: {e.response.text}", status_code=e.response.status_code)
    
    def list(self) -> List[Workflow]:
        """
        List all workflows.
        
        Returns:
            List of Workflow objects
        
        Raises:
            SunaError: If request fails
        """
        try:
            response = self._client.get(f"{self._base_url}/workflows")
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                workflows_data = data
            elif isinstance(data, dict) and "workflows" in data:
                workflows_data = data["workflows"]
            elif isinstance(data, dict) and "data" in data:
                workflows_data = data["data"]
            else:
                workflows_data = [data] if data else []
            
            return [Workflow(**workflow) for workflow in workflows_data]
        except httpx.HTTPStatusError as e:
            raise SunaError(f"Failed to list workflows: {e.response.text}", status_code=e.response.status_code)
    
    def update(self, workflow_id: str, definition: Dict[str, Any]) -> Workflow:
        """
        Update a workflow.
        
        Args:
            workflow_id: Workflow ID
            definition: New workflow definition
        
        Returns:
            Updated Workflow object
        
        Raises:
            NotFoundError: If workflow not found
            SunaError: If update fails
        """
        payload = {"definition": definition}
        
        try:
            response = self._client.put(f"{self._base_url}/workflows/{workflow_id}", json=payload)
            response.raise_for_status()
            return Workflow(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to update workflow: {e.response.text}", status_code=e.response.status_code)
    
    def delete(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            True if deleted successfully
        
        Raises:
            NotFoundError: If workflow not found
            SunaError: If deletion fails
        """
        try:
            response = self._client.delete(f"{self._base_url}/workflows/{workflow_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to delete workflow: {e.response.text}", status_code=e.response.status_code)
    
    def run(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None) -> WorkflowRun:
        """
        Execute a workflow.
        
        Args:
            workflow_id: Workflow ID
            inputs: Input parameters for the workflow
        
        Returns:
            WorkflowRun object
        
        Raises:
            NotFoundError: If workflow not found
            SunaError: If execution fails
        """
        payload = {"inputs": inputs or {}}
        
        try:
            response = self._client.post(f"{self._base_url}/workflows/{workflow_id}/run", json=payload)
            response.raise_for_status()
            return WorkflowRun(**response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(f"Workflow {workflow_id} not found")
            raise SunaError(f"Failed to run workflow: {e.response.text}", status_code=e.response.status_code)
