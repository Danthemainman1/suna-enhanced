"""
Task scheduler and background execution system for Suna Ultra.

This module provides comprehensive task scheduling with:
- Cron-like scheduling
- Background task execution with worker pools
- Multi-channel notifications (webhook, email, Slack, Discord)
- Task dependencies and priority queuing
- Retry logic with exponential backoff
- Persistent task state
"""

from .models import (
    CronExpression,
    ScheduledTask,
    BackgroundTask,
    TaskStatus,
    TaskStatusInfo,
    TaskResult,
    TaskEvent,
    TaskEventType,
    NotificationChannel,
    NotificationChannelType,
    WebhookConfig,
    EmailConfig,
    SMTPConfig,
    SlackConfig,
    DiscordConfig,
    CreateScheduleRequest,
    SubmitTaskRequest,
    TaskListResponse,
    ScheduleListResponse,
)

from .task_scheduler import TaskScheduler
from .background_executor import BackgroundExecutor
from .notification_service import NotificationService
from .api import router, initialize, cleanup


__all__ = [
    # Models
    "CronExpression",
    "ScheduledTask",
    "BackgroundTask",
    "TaskStatus",
    "TaskStatusInfo",
    "TaskResult",
    "TaskEvent",
    "TaskEventType",
    "NotificationChannel",
    "NotificationChannelType",
    "WebhookConfig",
    "EmailConfig",
    "SMTPConfig",
    "SlackConfig",
    "DiscordConfig",
    "CreateScheduleRequest",
    "SubmitTaskRequest",
    "TaskListResponse",
    "ScheduleListResponse",
    
    # Components
    "TaskScheduler",
    "BackgroundExecutor",
    "NotificationService",
    
    # API
    "router",
    "initialize",
    "cleanup",
]

__version__ = "1.0.0"
