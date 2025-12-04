"""
Proactive agent system for autonomous monitoring and triggering.
"""

from .models import (
    Monitor,
    MonitorEvent,
    Trigger,
    TriggerEvent,
    TriggerType,
    ScheduledTask,
    ScheduledTaskRun,
    Webhook,
    WebhookEvent,
    TaskSuggestion,
    PatternAnalysis,
)

from .monitor import ProactiveMonitor
from .triggers import TriggerManager
from .scheduler import Scheduler
from .webhooks import WebhookManager
from .suggestions import SuggestionEngine

# Import router only when not testing to avoid dependency issues
try:
    from .api import router
except ImportError:
    router = None

__all__ = [
    "Monitor",
    "MonitorEvent",
    "Trigger",
    "TriggerEvent",
    "TriggerType",
    "ScheduledTask",
    "ScheduledTaskRun",
    "Webhook",
    "WebhookEvent",
    "TaskSuggestion",
    "PatternAnalysis",
    "ProactiveMonitor",
    "TriggerManager",
    "Scheduler",
    "WebhookManager",
    "SuggestionEngine",
    "router",
]
