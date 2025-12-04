"""
Pydantic models for multi-agent collaboration.

This module defines data models for collaboration modes, configurations,
and results.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


# Enums
class CollaborationMode(str, Enum):
    """Type of collaboration mode."""
    DEBATE = "debate"
    ENSEMBLE = "ensemble"
    PIPELINE = "pipeline"
    SWARM = "swarm"
    CRITIQUE = "critique"


class MergeStrategy(str, Enum):
    """Strategy for merging ensemble results."""
    VOTE = "vote"
    AVERAGE = "average"
    LLM_SYNTHESIS = "llm_synthesis"


class CoordinationStrategy(str, Enum):
    """Strategy for swarm coordination."""
    BLACKBOARD = "blackboard"
    MESSAGE_PASSING = "message_passing"


class HandoffFormat(str, Enum):
    """Format for pipeline handoffs."""
    STRUCTURED = "structured"
    NATURAL = "natural"


# Result Models
class CollaborationResult(BaseModel):
    """Result from a multi-agent collaboration."""
    
    mode: str = Field(..., description="Collaboration mode used")
    agents_used: list[str] = Field(..., description="List of agent IDs that participated")
    final_output: Any = Field(..., description="Final collaborative output")
    individual_outputs: list[dict] = Field(default_factory=list, description="Individual agent outputs")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When collaboration started")
    completed_at: Optional[datetime] = Field(None, description="When collaboration completed")


# Configuration Models
class DebateConfig(BaseModel):
    """Configuration for debate mode."""
    
    rounds: int = Field(3, ge=1, le=10, description="Number of debate rounds")
    judge_agent_id: Optional[str] = Field(None, description="ID of judge agent (None = use Claude)")
    time_limit_per_round_sec: int = Field(300, description="Time limit per round in seconds")


class EnsembleConfig(BaseModel):
    """Configuration for ensemble mode."""
    
    merge_strategy: MergeStrategy = Field(MergeStrategy.VOTE, description="Strategy for merging results")
    min_agreement: float = Field(0.5, ge=0.0, le=1.0, description="Minimum agreement threshold")
    parallel_execution: bool = Field(True, description="Execute agents in parallel")


class PipelineConfig(BaseModel):
    """Configuration for pipeline mode."""
    
    handoff_format: HandoffFormat = Field(HandoffFormat.STRUCTURED, description="Format for handoffs")
    allow_backtrack: bool = Field(False, description="Allow pipeline to backtrack on errors")
    timeout_per_stage_sec: int = Field(600, description="Timeout per pipeline stage in seconds")


class SwarmConfig(BaseModel):
    """Configuration for swarm mode."""
    
    max_agents: int = Field(10, ge=1, le=100, description="Maximum number of agents in swarm")
    allow_spawn: bool = Field(True, description="Allow agents to spawn helpers")
    coordination: CoordinationStrategy = Field(
        CoordinationStrategy.BLACKBOARD,
        description="Coordination strategy"
    )
    convergence_threshold: float = Field(0.8, description="Threshold for task completion")


class CritiqueConfig(BaseModel):
    """Configuration for critique mode."""
    
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum improvement iterations")
    approval_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Approval score threshold")
    parallel_review: bool = Field(True, description="Critics review in parallel")


# Task and Agent Models
class CollaborationTask(BaseModel):
    """A task for multi-agent collaboration."""
    
    id: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")
    requirements: list[str] = Field(default_factory=list, description="Task requirements")
    constraints: dict = Field(default_factory=dict, description="Task constraints")
    context: dict = Field(default_factory=dict, description="Additional context")


class AgentRole(str, Enum):
    """Role an agent can play in collaboration."""
    PRIMARY = "primary"
    CRITIC = "critic"
    JUDGE = "judge"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"


class CollaborationAgent(BaseModel):
    """An agent participating in collaboration."""
    
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    role: AgentRole = Field(AgentRole.SPECIALIST, description="Agent's role")
    capabilities: list[str] = Field(default_factory=list, description="Agent capabilities")
    position: Optional[str] = Field(None, description="Position in debate (pro/con)")


# Debate Models
class DebateArgument(BaseModel):
    """An argument in a debate."""
    
    agent_id: str = Field(..., description="Agent making the argument")
    round: int = Field(..., description="Debate round number")
    position: str = Field(..., description="Position being argued (pro/con)")
    argument: str = Field(..., description="The argument text")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When argument was made")


class DebateResult(BaseModel):
    """Result of a debate."""
    
    winner: str = Field(..., description="Winning position")
    winning_agent_id: str = Field(..., description="ID of winning agent")
    arguments: list[DebateArgument] = Field(default_factory=list, description="All arguments")
    judge_reasoning: str = Field(..., description="Judge's reasoning for decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in decision")


# Ensemble Models
class EnsembleVote(BaseModel):
    """A vote from an ensemble agent."""
    
    agent_id: str = Field(..., description="Agent ID")
    output: Any = Field(..., description="Agent's output")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent's confidence")
    reasoning: Optional[str] = Field(None, description="Reasoning for output")


# Pipeline Models
class PipelineStage(BaseModel):
    """A stage in a pipeline."""
    
    stage_number: int = Field(..., description="Stage sequence number")
    agent_id: str = Field(..., description="Agent handling this stage")
    input_data: dict = Field(..., description="Input to this stage")
    output_data: Optional[dict] = Field(None, description="Output from this stage")
    status: str = Field("pending", description="Stage status")
    started_at: Optional[datetime] = Field(None, description="When stage started")
    completed_at: Optional[datetime] = Field(None, description="When stage completed")


# Swarm Models
class SubTask(BaseModel):
    """A subtask in swarm decomposition."""
    
    id: str = Field(..., description="Subtask ID")
    description: str = Field(..., description="Subtask description")
    claimed_by: Optional[str] = Field(None, description="Agent ID that claimed this subtask")
    status: str = Field("pending", description="Subtask status")
    result: Optional[Any] = Field(None, description="Subtask result")
    dependencies: list[str] = Field(default_factory=list, description="Dependent subtask IDs")


class BlackboardMessage(BaseModel):
    """A message on the swarm blackboard."""
    
    id: str = Field(..., description="Message ID")
    from_agent: str = Field(..., description="Sender agent ID")
    message_type: str = Field(..., description="Type of message")
    content: dict = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When message was posted")


# Critique Models
class CritiqueReview(BaseModel):
    """A review from a critic agent."""
    
    critic_id: str = Field(..., description="Critic agent ID")
    iteration: int = Field(..., description="Iteration number")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    feedback: str = Field(..., description="Detailed feedback")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When review was made")


class CritiqueIteration(BaseModel):
    """An iteration in the critique process."""
    
    iteration_number: int = Field(..., description="Iteration sequence number")
    primary_output: Any = Field(..., description="Output from primary agent")
    reviews: list[CritiqueReview] = Field(default_factory=list, description="Reviews from critics")
    average_score: float = Field(..., description="Average score from all reviews")
    approved: bool = Field(False, description="Whether output was approved")
