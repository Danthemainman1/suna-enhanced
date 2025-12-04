"""
Pydantic models for agent debugging system.

This module defines all data models for debugging sessions, execution snapshots,
graphs, and AI-powered explanations.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


# Enums
class DebugStatus(str, Enum):
    """Status of a debug session."""
    PAUSED = "paused"
    RUNNING = "running"
    COMPLETED = "completed"
    DETACHED = "detached"


class StepType(str, Enum):
    """Type of execution step."""
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    DECISION = "decision"
    OUTPUT = "output"
    ERROR = "error"


class GraphNodeType(str, Enum):
    """Type of execution graph node."""
    START = "start"
    THINKING = "thinking"
    DECISION = "decision"
    TOOL_CALL = "tool_call"
    OUTPUT = "output"
    ERROR = "error"
    END = "end"


class Priority(str, Enum):
    """Priority level for suggestions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Debug Session Models
class DebugSession(BaseModel):
    """Represents an active debugging session."""
    
    id: str = Field(..., description="Unique session identifier")
    agent_id: str = Field(..., description="ID of the agent being debugged")
    task_id: str = Field(..., description="ID of the task being debugged")
    status: DebugStatus = Field(..., description="Current session status")
    current_step: int = Field(0, description="Current step number")
    total_steps: int = Field(0, description="Total number of steps")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")


class DebugState(BaseModel):
    """Represents the state at a specific execution step."""
    
    step_number: int = Field(..., description="Step sequence number")
    step_type: StepType = Field(..., description="Type of step")
    description: str = Field(..., description="Human-readable description")
    input_data: dict = Field(default_factory=dict, description="Input data for this step")
    output_data: Optional[dict] = Field(None, description="Output data from this step")
    variables: dict = Field(default_factory=dict, description="Variables in scope")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When step executed")


# Time Travel Models
class ExecutionSnapshot(BaseModel):
    """Represents a snapshot of execution state at a point in time."""
    
    id: str = Field(..., description="Unique snapshot identifier")
    task_id: str = Field(..., description="ID of the task")
    step_number: int = Field(..., description="Step sequence number")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When snapshot was taken")
    state: dict = Field(default_factory=dict, description="Complete state at this point")
    action: str = Field(..., description="Action that was performed")
    result: Optional[dict] = Field(None, description="Result of the action")


class ReplaySession(BaseModel):
    """Represents a time-travel replay session."""
    
    id: str = Field(..., description="Unique replay session ID")
    task_id: str = Field(..., description="ID of the original task")
    current_snapshot_index: int = Field(0, description="Current position in replay")
    total_snapshots: int = Field(..., description="Total number of snapshots")
    snapshots: list[ExecutionSnapshot] = Field(default_factory=list, description="All snapshots in order")


# Execution Graph Models
class GraphNode(BaseModel):
    """Represents a node in the execution graph."""
    
    id: str = Field(..., description="Unique node identifier")
    type: GraphNodeType = Field(..., description="Type of node")
    label: str = Field(..., description="Display label")
    data: dict = Field(default_factory=dict, description="Associated data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Node creation time")


class GraphEdge(BaseModel):
    """Represents an edge connecting two nodes in the execution graph."""
    
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label")


class ExecutionGraph(BaseModel):
    """Represents the complete execution graph for a task."""
    
    task_id: str = Field(..., description="ID of the task")
    nodes: list[GraphNode] = Field(default_factory=list, description="All nodes in the graph")
    edges: list[GraphEdge] = Field(default_factory=list, description="All edges in the graph")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


# AI Explainer Models
class Explanation(BaseModel):
    """AI-generated explanation of an agent decision."""
    
    summary: str = Field(..., description="Brief summary of the decision")
    reasoning_chain: list[str] = Field(default_factory=list, description="Step-by-step reasoning")
    key_factors: list[str] = Field(default_factory=list, description="Key factors that influenced decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in explanation")
    alternatives_considered: list[str] = Field(default_factory=list, description="Alternative approaches considered")


class FailureExplanation(BaseModel):
    """AI-generated explanation of why a task failed."""
    
    error_type: str = Field(..., description="Type of error that occurred")
    root_cause: str = Field(..., description="Root cause of the failure")
    contributing_factors: list[str] = Field(default_factory=list, description="Contributing factors")
    suggestions: list[str] = Field(default_factory=list, description="Suggestions for fixing")


class Suggestion(BaseModel):
    """AI-generated improvement suggestion."""
    
    title: str = Field(..., description="Brief title")
    description: str = Field(..., description="Detailed description")
    priority: Priority = Field(..., description="Priority level")
    implementation: Optional[str] = Field(None, description="Implementation guidance")


# Breakpoint Models
class BreakpointType(str, Enum):
    """Type of breakpoint."""
    STEP = "step"  # Break at specific step number
    CONDITION = "condition"  # Break when condition is true
    TOOL = "tool"  # Break before/after tool call
    ERROR = "error"  # Break on error


class Breakpoint(BaseModel):
    """Represents a debugging breakpoint."""
    
    id: str = Field(..., description="Unique breakpoint ID")
    session_id: str = Field(..., description="Debug session ID")
    type: BreakpointType = Field(..., description="Type of breakpoint")
    condition: Optional[str] = Field(None, description="Condition expression (for conditional breakpoints)")
    step_number: Optional[int] = Field(None, description="Step number (for step breakpoints)")
    tool_name: Optional[str] = Field(None, description="Tool name (for tool breakpoints)")
    enabled: bool = Field(True, description="Whether breakpoint is active")
    hit_count: int = Field(0, description="Number of times hit")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
