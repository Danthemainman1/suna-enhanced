"""
Pydantic models for proactive agent system.

This module defines all data models for monitors, triggers, schedules,
webhooks, and suggestions.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class TriggerType(str, Enum):
    """Types of triggers that can fire agents."""
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    EMAIL = "email"
    SLACK = "slack"
    GITHUB = "github"


# ===== MONITOR MODELS =====

class Monitor(BaseModel):
    """A monitor that continuously checks conditions and triggers actions."""
    id: str = Field(..., description="Unique monitor identifier")
    name: str = Field(..., description="Human-readable monitor name")
    agent_id: str = Field(..., description="Agent to trigger when condition met")
    workspace_id: str = Field(..., description="Workspace this monitor belongs to")
    condition: str = Field(..., description="Condition to monitor (natural language or expression)")
    action: str = Field(..., description="Action the agent should perform when triggered")
    check_interval: int = Field(300, description="Seconds between condition checks")
    is_active: bool = Field(True, description="Whether monitor is currently active")
    last_check: Optional[datetime] = Field(None, description="When monitor last checked condition")
    last_triggered: Optional[datetime] = Field(None, description="When monitor last triggered action")
    trigger_count: int = Field(0, description="Number of times monitor has triggered")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When monitor was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When monitor was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MonitorEvent(BaseModel):
    """An event representing a monitor check or trigger."""
    id: str = Field(..., description="Unique event identifier")
    monitor_id: str = Field(..., description="Related monitor ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When event occurred")
    condition_met: bool = Field(..., description="Whether condition was met")
    triggered: bool = Field(..., description="Whether action was triggered")
    task_id: Optional[str] = Field(None, description="Task ID if action was triggered")
    result_data: Dict[str, Any] = Field(default_factory=dict, description="Event result data")
    error: Optional[str] = Field(None, description="Error message if any")


# ===== TRIGGER MODELS =====

class Trigger(BaseModel):
    """A trigger that fires an agent when events occur."""
    id: str = Field(..., description="Unique trigger identifier")
    name: str = Field(..., description="Human-readable trigger name")
    workspace_id: str = Field(..., description="Workspace this trigger belongs to")
    trigger_type: TriggerType = Field(..., description="Type of trigger")
    config: Dict[str, Any] = Field(..., description="Trigger-specific configuration")
    agent_id: str = Field(..., description="Agent to trigger")
    task_template: str = Field(..., description="Task description template with variables")
    is_active: bool = Field(True, description="Whether trigger is currently active")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When trigger was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When trigger was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TriggerEvent(BaseModel):
    """An event representing a trigger firing."""
    id: str = Field(..., description="Unique event identifier")
    trigger_id: str = Field(..., description="Related trigger ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When event occurred")
    payload: Dict[str, Any] = Field(..., description="Event payload data")
    task_id: Optional[str] = Field(None, description="Task ID if agent was triggered")
    success: bool = Field(..., description="Whether trigger fired successfully")
    error: Optional[str] = Field(None, description="Error message if any")


# ===== SCHEDULED TASK MODELS =====

class ScheduledTask(BaseModel):
    """A task scheduled to run at specific times."""
    id: str = Field(..., description="Unique schedule identifier")
    name: str = Field(..., description="Human-readable task name")
    workspace_id: str = Field(..., description="Workspace this schedule belongs to")
    agent_id: str = Field(..., description="Agent to run")
    task_description: str = Field(..., description="Task description to pass to agent")
    cron_expression: str = Field(..., description="Cron expression for schedule")
    timezone: str = Field("UTC", description="Timezone for schedule")
    is_active: bool = Field(True, description="Whether schedule is currently active")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run time")
    last_run: Optional[datetime] = Field(None, description="Last run time")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When schedule was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When schedule was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ScheduledTaskRun(BaseModel):
    """A record of a scheduled task execution."""
    id: str = Field(..., description="Unique run identifier")
    schedule_id: str = Field(..., description="Related schedule ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When run occurred")
    task_id: Optional[str] = Field(None, description="Task ID if agent was triggered")
    success: bool = Field(..., description="Whether run was successful")
    error: Optional[str] = Field(None, description="Error message if any")


# ===== WEBHOOK MODELS =====

class Webhook(BaseModel):
    """An incoming webhook endpoint."""
    id: str = Field(..., description="Unique webhook identifier")
    workspace_id: str = Field(..., description="Workspace this webhook belongs to")
    name: str = Field(..., description="Human-readable webhook name")
    url_path: str = Field(..., description="Unique URL path for webhook")
    secret: str = Field(..., description="Secret for signature verification")
    trigger_id: str = Field(..., description="Trigger to fire when webhook received")
    is_active: bool = Field(True, description="Whether webhook is currently active")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When webhook was created")
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When webhook was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WebhookEvent(BaseModel):
    """An event representing a webhook invocation."""
    id: str = Field(..., description="Unique event identifier")
    webhook_id: str = Field(..., description="Related webhook ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When event occurred")
    payload: Dict[str, Any] = Field(..., description="Webhook payload")
    headers: Dict[str, str] = Field(..., description="Request headers")
    task_id: Optional[str] = Field(None, description="Task ID if trigger was fired")
    success: bool = Field(..., description="Whether webhook was processed successfully")
    error: Optional[str] = Field(None, description="Error message if any")


# ===== SUGGESTION MODELS =====

class TaskSuggestion(BaseModel):
    """An AI-generated task suggestion based on patterns."""
    id: str = Field(..., description="Unique suggestion identifier")
    workspace_id: str = Field(..., description="Workspace this suggestion belongs to")
    user_id: str = Field(..., description="User this suggestion is for")
    title: str = Field(..., description="Suggestion title")
    description: str = Field(..., description="Detailed suggestion description")
    suggested_agent_id: str = Field(..., description="Suggested agent to use")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reason: str = Field(..., description="Why this task is suggested")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When suggestion was created")
    dismissed: bool = Field(False, description="Whether user dismissed this suggestion")
    accepted: bool = Field(False, description="Whether user accepted this suggestion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PatternAnalysis(BaseModel):
    """Analysis of user patterns for generating suggestions."""
    workspace_id: str = Field(..., description="Workspace analyzed")
    user_id: str = Field(..., description="User analyzed")
    analysis_date: datetime = Field(default_factory=lambda: datetime.utcnow(), description="When analysis was performed")
    patterns: Dict[str, Any] = Field(..., description="Detected patterns")
    insights: List[str] = Field(..., description="Key insights from analysis")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ===== REQUEST/RESPONSE MODELS =====

class CreateMonitorRequest(BaseModel):
    """Request to create a monitor."""
    name: str = Field(..., description="Monitor name")
    agent_id: str = Field(..., description="Agent to trigger")
    workspace_id: str = Field(..., description="Workspace ID")
    condition: str = Field(..., description="Condition to monitor")
    action: str = Field(..., description="Action to perform")
    check_interval: int = Field(300, description="Check interval in seconds")


class UpdateMonitorRequest(BaseModel):
    """Request to update a monitor."""
    name: Optional[str] = Field(None, description="Monitor name")
    condition: Optional[str] = Field(None, description="Condition to monitor")
    action: Optional[str] = Field(None, description="Action to perform")
    check_interval: Optional[int] = Field(None, description="Check interval in seconds")
    is_active: Optional[bool] = Field(None, description="Whether monitor is active")


class CreateTriggerRequest(BaseModel):
    """Request to create a trigger."""
    name: str = Field(..., description="Trigger name")
    workspace_id: str = Field(..., description="Workspace ID")
    trigger_type: TriggerType = Field(..., description="Type of trigger")
    config: Dict[str, Any] = Field(..., description="Trigger configuration")
    agent_id: str = Field(..., description="Agent to trigger")
    task_template: str = Field(..., description="Task template")


class CreateScheduleRequest(BaseModel):
    """Request to create a scheduled task."""
    name: str = Field(..., description="Task name")
    workspace_id: str = Field(..., description="Workspace ID")
    agent_id: str = Field(..., description="Agent to run")
    task_description: str = Field(..., description="Task description")
    cron_expression: str = Field(..., description="Cron expression")
    timezone: str = Field("UTC", description="Timezone")


class CreateWebhookRequest(BaseModel):
    """Request to create a webhook."""
    workspace_id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Webhook name")
    trigger_id: str = Field(..., description="Trigger to fire")


class FireTriggerRequest(BaseModel):
    """Request to manually fire a trigger."""
    payload: Dict[str, Any] = Field(default_factory=dict, description="Trigger payload")
