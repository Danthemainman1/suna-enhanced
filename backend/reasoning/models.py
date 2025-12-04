"""
Pydantic models for reasoning engines.

This module defines all data models used by the reasoning engines including
Chain-of-Thought, Tree-of-Thoughts, ReAct, and self-reflection.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


# Chain-of-Thought Models
class ReasoningStep(BaseModel):
    """A single step in a reasoning chain."""
    
    step_number: int = Field(..., description="Step sequence number")
    thought: str = Field(..., description="The reasoning thought for this step")
    observation: Optional[str] = Field(None, description="Observation from this step")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in this step (0-1)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this step occurred")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional step metadata")


class ReasoningResult(BaseModel):
    """Result from chain-of-thought reasoning."""
    
    problem: str = Field(..., description="The original problem statement")
    steps: list[ReasoningStep] = Field(default_factory=list, description="Sequence of reasoning steps")
    conclusion: str = Field(..., description="Final conclusion or answer")
    total_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence in result")
    reasoning_type: str = Field("chain_of_thought", description="Type of reasoning used")
    duration_seconds: float = Field(0.0, description="Time taken for reasoning")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")


# Tree-of-Thoughts Models
class ThoughtNode(BaseModel):
    """A node in the tree of thoughts."""
    
    node_id: str = Field(..., description="Unique node identifier")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    depth: int = Field(0, description="Depth in the tree")
    thought: str = Field(..., description="The thought content")
    score: float = Field(0.0, description="Score/quality of this thought")
    is_terminal: bool = Field(False, description="Whether this is a leaf node")
    children: list[str] = Field(default_factory=list, description="Child node IDs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional node metadata")


class ToTResult(BaseModel):
    """Result from tree-of-thoughts exploration."""
    
    problem: str = Field(..., description="The original problem statement")
    nodes: dict[str, ThoughtNode] = Field(default_factory=dict, description="All explored nodes")
    best_path: list[str] = Field(default_factory=list, description="Node IDs of best path")
    best_score: float = Field(0.0, description="Score of best path")
    exploration_strategy: str = Field("breadth_first", description="Strategy used for exploration")
    nodes_explored: int = Field(0, description="Total nodes explored")
    max_depth_reached: int = Field(0, description="Maximum depth reached")
    duration_seconds: float = Field(0.0, description="Time taken for exploration")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")


# ReAct Models
class Action(BaseModel):
    """An action that can be taken."""
    
    action_id: str = Field(..., description="Unique action identifier")
    name: str = Field(..., description="Action name")
    description: str = Field(..., description="What this action does")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    requires_context: list[str] = Field(default_factory=list, description="Required context keys")


class Observation(BaseModel):
    """Observation from executing an action."""
    
    action_id: str = Field(..., description="ID of action that produced this")
    success: bool = Field(..., description="Whether action succeeded")
    result: Any = Field(None, description="Action result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When observed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ReActStep(BaseModel):
    """A step in the ReAct (Reasoning + Acting) loop."""
    
    step_number: int = Field(..., description="Step sequence number")
    thought: str = Field(..., description="Reasoning about what to do next")
    action: Optional[Action] = Field(None, description="Action taken (if any)")
    observation: Optional[Observation] = Field(None, description="Observation from action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this step occurred")


class ReActResult(BaseModel):
    """Result from ReAct loop execution."""
    
    goal: str = Field(..., description="The goal that was pursued")
    steps: list[ReActStep] = Field(default_factory=list, description="Sequence of ReAct steps")
    goal_achieved: bool = Field(False, description="Whether the goal was achieved")
    final_answer: Optional[str] = Field(None, description="Final answer or result")
    iterations_used: int = Field(0, description="Number of iterations executed")
    duration_seconds: float = Field(0.0, description="Time taken")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Self-Reflection Models
class Critique(BaseModel):
    """A critique of an output."""
    
    critique_id: str = Field(..., description="Unique critique identifier")
    output: str = Field(..., description="The output being critiqued")
    issues: list[str] = Field(default_factory=list, description="List of identified issues")
    strengths: list[str] = Field(default_factory=list, description="List of strengths")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
    overall_quality: float = Field(0.0, ge=0.0, le=1.0, description="Overall quality score (0-1)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When critique was made")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ReflectionResult(BaseModel):
    """Result from self-reflection process."""
    
    original_output: str = Field(..., description="The original output")
    critique: Critique = Field(..., description="Critique of the output")
    improved_output: Optional[str] = Field(None, description="Improved version (if generated)")
    reflection_iterations: int = Field(1, description="Number of reflection iterations")
    improvement_score: float = Field(0.0, description="How much better the improved version is")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When reflection completed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Feedback Loop Models
class Strategy(BaseModel):
    """An agent strategy for task execution."""
    
    strategy_id: str = Field(..., description="Unique strategy identifier")
    agent_id: str = Field(..., description="Agent this strategy is for")
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="What this strategy does")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    success_rate: float = Field(0.0, ge=0.0, le=1.0, description="Historical success rate")
    usage_count: int = Field(0, description="Number of times used")
    last_used: Optional[datetime] = Field(None, description="When last used")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskOutcome(BaseModel):
    """Outcome of a task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    agent_id: str = Field(..., description="Agent that executed the task")
    strategy_id: Optional[str] = Field(None, description="Strategy used (if any)")
    success: bool = Field(..., description="Whether task succeeded")
    metrics: dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When task completed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Prompt Optimization Models
class PromptStats(BaseModel):
    """Statistics for a prompt."""
    
    prompt_id: str = Field(..., description="Unique prompt identifier")
    prompt_text: str = Field(..., description="The prompt text")
    usage_count: int = Field(0, description="Number of times used")
    success_count: int = Field(0, description="Number of successful uses")
    success_rate: float = Field(0.0, ge=0.0, le=1.0, description="Success rate")
    average_score: float = Field(0.0, description="Average quality score")
    average_duration: float = Field(0.0, description="Average execution time")
    last_used: Optional[datetime] = Field(None, description="When last used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When created")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PromptVariation(BaseModel):
    """A variation of a prompt for optimization."""
    
    variation_id: str = Field(..., description="Unique variation identifier")
    base_prompt_id: str = Field(..., description="ID of base prompt")
    prompt_text: str = Field(..., description="The variation text")
    variation_type: str = Field(..., description="Type of variation (e.g., 'rephrased', 'detailed')")
    stats: Optional[PromptStats] = Field(None, description="Statistics for this variation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
