"""
Pydantic models for task scheduler and background execution.

This module defines all data models for scheduling, task execution,
and notifications.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Any, Optional, Literal
from datetime import datetime
from enum import Enum


# Enums
class TaskStatus(str, Enum):
    """Status of a background task."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskEventType(str, Enum):
    """Types of task events for notifications."""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    RESUMED = "resumed"
    CANCELLED = "cancelled"
    PROGRESS_UPDATE = "progress_update"


class NotificationChannelType(str, Enum):
    """Types of notification channels."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"


# Scheduler Models
class CronExpression(BaseModel):
    """Cron expression for scheduling."""
    
    expression: str = Field(..., description="Cron expression (e.g., '0 0 * * *')")
    timezone: str = Field("UTC", description="Timezone for schedule")
    
    def __str__(self) -> str:
        return f"{self.expression} ({self.timezone})"


class ScheduledTask(BaseModel):
    """A scheduled task configuration."""
    
    schedule_id: str = Field(..., description="Unique schedule identifier")
    name: str = Field(..., description="Human-readable task name")
    description: Optional[str] = Field(None, description="Task description")
    cron_expression: Optional[CronExpression] = Field(None, description="Cron schedule")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run time")
    last_run: Optional[datetime] = Field(None, description="Last run time")
    enabled: bool = Field(True, description="Whether schedule is active")
    task_definition: dict[str, Any] = Field(..., description="Task configuration to execute")
    max_retries: int = Field(3, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(60, description="Delay between retries")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last updated")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Background Task Models
class BackgroundTask(BaseModel):
    """A background task to execute."""
    
    task_id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_type: str = Field(..., description="Type of task")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: int = Field(5, ge=1, le=10, description="Priority (1=lowest, 10=highest)")
    max_retries: int = Field(3, description="Maximum retry attempts")
    retry_count: int = Field(0, description="Current retry count")
    timeout_seconds: Optional[int] = Field(None, description="Task timeout")
    dependencies: list[str] = Field(default_factory=list, description="Task IDs this depends on")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When created")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskResult(BaseModel):
    """Result from task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether task succeeded")
    result: Optional[Any] = Field(None, description="Task result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(..., description="When task started")
    completed_at: datetime = Field(..., description="When task completed")
    duration_seconds: float = Field(..., description="Execution duration")
    retry_count: int = Field(0, description="Number of retries attempted")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskStatusInfo(BaseModel):
    """Current status information for a task."""
    
    task_id: str = Field(..., description="Task identifier")
    name: str = Field(..., description="Task name")
    status: TaskStatus = Field(..., description="Current status")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0-1)")
    created_at: datetime = Field(..., description="When task was created")
    started_at: Optional[datetime] = Field(None, description="When task started")
    updated_at: datetime = Field(..., description="Last status update")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    result: Optional[TaskResult] = Field(None, description="Result if completed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Notification Models
class WebhookConfig(BaseModel):
    """Webhook notification configuration."""
    
    url: str = Field(..., description="Webhook URL")
    secret: Optional[str] = Field(None, description="Webhook secret for signing")
    headers: dict[str, str] = Field(default_factory=dict, description="Custom headers")
    timeout_seconds: int = Field(30, description="Request timeout")


class SMTPConfig(BaseModel):
    """SMTP email configuration."""
    
    host: str = Field(..., description="SMTP server host")
    port: int = Field(587, description="SMTP server port")
    username: str = Field(..., description="SMTP username")
    password: str = Field(..., description="SMTP password")
    from_email: EmailStr = Field(..., description="From email address")
    use_tls: bool = Field(True, description="Use TLS")
    use_ssl: bool = Field(False, description="Use SSL")


class EmailConfig(BaseModel):
    """Email notification configuration."""
    
    smtp: SMTPConfig = Field(..., description="SMTP configuration")
    to_emails: list[EmailStr] = Field(..., description="Recipient email addresses")
    subject_template: str = Field(..., description="Email subject template")
    body_template: str = Field(..., description="Email body template")


class SlackConfig(BaseModel):
    """Slack notification configuration."""
    
    webhook_url: str = Field(..., description="Slack webhook URL")
    channel: Optional[str] = Field(None, description="Slack channel")
    username: Optional[str] = Field("Suna Ultra", description="Bot username")
    icon_emoji: Optional[str] = Field(":robot_face:", description="Bot icon emoji")


class DiscordConfig(BaseModel):
    """Discord notification configuration."""
    
    webhook_url: str = Field(..., description="Discord webhook URL")
    username: Optional[str] = Field("Suna Ultra", description="Bot username")
    avatar_url: Optional[str] = Field(None, description="Bot avatar URL")


class NotificationChannel(BaseModel):
    """A notification channel configuration."""
    
    channel_type: NotificationChannelType = Field(..., description="Type of channel")
    webhook_config: Optional[WebhookConfig] = Field(None, description="Webhook config")
    email_config: Optional[EmailConfig] = Field(None, description="Email config")
    slack_config: Optional[SlackConfig] = Field(None, description="Slack config")
    discord_config: Optional[DiscordConfig] = Field(None, description="Discord config")
    enabled: bool = Field(True, description="Whether channel is enabled")


class TaskEvent(BaseModel):
    """An event related to a task."""
    
    event_id: str = Field(..., description="Unique event identifier")
    task_id: str = Field(..., description="Related task ID")
    event_type: TaskEventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When event occurred")
    data: dict[str, Any] = Field(default_factory=dict, description="Event data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# API Request/Response Models
class CreateScheduleRequest(BaseModel):
    """Request to create a scheduled task."""
    
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    cron_expression: str = Field(..., description="Cron expression")
    timezone: str = Field("UTC", description="Timezone")
    task_definition: dict[str, Any] = Field(..., description="Task configuration")
    max_retries: int = Field(3, description="Maximum retries")
    enabled: bool = Field(True, description="Start enabled")


class SubmitTaskRequest(BaseModel):
    """Request to submit a background task."""
    
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Task description")
    task_type: str = Field(..., description="Type of task")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    priority: int = Field(5, ge=1, le=10, description="Priority")
    max_retries: int = Field(3, description="Maximum retries")
    timeout_seconds: Optional[int] = Field(None, description="Timeout")
    dependencies: list[str] = Field(default_factory=list, description="Dependencies")


class TaskListResponse(BaseModel):
    """Response with list of tasks."""
    
    tasks: list[TaskStatusInfo] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")


class ScheduleListResponse(BaseModel):
    """Response with list of schedules."""
    
    schedules: list[ScheduledTask] = Field(..., description="List of schedules")
    total: int = Field(..., description="Total number of schedules")
    page: int = Field(1, description="Current page")
    page_size: int = Field(20, description="Page size")
