"""Data models for Suna Ultra SDK."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Agent(BaseModel):
    """Represents an AI agent."""
    
    model_config = ConfigDict(extra="allow")
    
    agent_id: str = Field(..., alias="agent_id")
    name: str
    type: Optional[str] = None
    status: Optional[str] = None
    capabilities: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """Represents a task submitted to an agent."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str
    agent_id: str
    description: str
    status: str
    priority: int = 5
    context: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResult(BaseModel):
    """Represents the result of a completed task."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str
    task_id: str
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    completed_at: Optional[datetime] = None


class TaskEvent(BaseModel):
    """Represents a streaming event from a task."""
    
    model_config = ConfigDict(extra="allow")
    
    event: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class Workflow(BaseModel):
    """Represents a workflow definition."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str
    name: str
    definition: Dict[str, Any]
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowRun(BaseModel):
    """Represents a workflow execution."""
    
    model_config = ConfigDict(extra="allow")
    
    id: str
    workflow_id: str
    status: str
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class Tool(BaseModel):
    """Represents a tool available to agents."""
    
    model_config = ConfigDict(extra="allow")
    
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ToolResult(BaseModel):
    """Represents the result of a tool execution."""
    
    model_config = ConfigDict(extra="allow")
    
    tool_name: str
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
