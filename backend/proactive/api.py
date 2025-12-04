"""
FastAPI router for proactive agent system.

This module provides REST API endpoints for monitors, triggers, schedules,
webhooks, and suggestions.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.responses import JSONResponse
from typing import Optional
from typing import List, Dict
from datetime import datetime

from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger

from .models import (
    Monitor,
    MonitorEvent,
    Trigger,
    ScheduledTask,
    Webhook,
    TaskSuggestion,
    CreateMonitorRequest,
    UpdateMonitorRequest,
    CreateTriggerRequest,
    CreateScheduleRequest,
    CreateWebhookRequest,
    FireTriggerRequest,
)

from .monitor import ProactiveMonitor
from .triggers import TriggerManager
from .scheduler import Scheduler
from .webhooks import WebhookManager
from .suggestions import SuggestionEngine


# Initialize components
router = APIRouter(prefix="/api/proactive", tags=["proactive"])

monitor_manager = ProactiveMonitor()
trigger_manager = TriggerManager()
scheduler = Scheduler()
webhook_manager = WebhookManager()
suggestion_engine = SuggestionEngine()


# ===== MONITOR ENDPOINTS =====

@router.post("/monitors", response_model=Monitor)
async def create_monitor(
    request: CreateMonitorRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Create a new monitor."""
    try:
        monitor = await monitor_manager.create(
            name=request.name,
            agent_id=request.agent_id,
            workspace_id=request.workspace_id,
            condition=request.condition,
            action=request.action,
            check_interval=request.check_interval
        )
        return monitor
    except Exception as e:
        logger.error(f"Error creating monitor: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/monitors", response_model=list[Monitor])
async def list_monitors(
    workspace_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """List all monitors for a workspace."""
    try:
        monitors = await monitor_manager.list(workspace_id)
        return monitors
    except Exception as e:
        logger.error(f"Error listing monitors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitors/{monitor_id}", response_model=Monitor)
async def get_monitor(
    monitor_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Get a specific monitor by ID."""
    monitor = await monitor_manager.get(monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.patch("/monitors/{monitor_id}", response_model=Monitor)
async def update_monitor(
    monitor_id: str,
    request: UpdateMonitorRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Update a monitor."""
    try:
        # Build update kwargs from request
        update_data = request.model_dump(exclude_unset=True)
        
        monitor = await monitor_manager.update(monitor_id, **update_data)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")
        
        return monitor
    except Exception as e:
        logger.error(f"Error updating monitor: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/monitors/{monitor_id}")
async def delete_monitor(
    monitor_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Delete a monitor."""
    success = await monitor_manager.delete(monitor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    return {"message": "Monitor deleted successfully"}


@router.post("/monitors/{monitor_id}/pause", response_model=Monitor)
async def pause_monitor(
    monitor_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Pause a monitor."""
    monitor = await monitor_manager.pause(monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.post("/monitors/{monitor_id}/resume", response_model=Monitor)
async def resume_monitor(
    monitor_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Resume a monitor."""
    monitor = await monitor_manager.resume(monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.post("/monitors/{monitor_id}/check", response_model=Optional[MonitorEvent])
async def check_monitor(
    monitor_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Manually trigger a monitor check."""
    event = await monitor_manager.check_now(monitor_id)
    if not event:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return event


@router.get("/monitors/{monitor_id}/history", response_model=list[MonitorEvent])
async def get_monitor_history(
    monitor_id: str,
    limit: int = 100,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Get monitor event history."""
    history = await monitor_manager.get_history(monitor_id, limit)
    return history


# ===== TRIGGER ENDPOINTS =====

@router.post("/triggers", response_model=Trigger)
async def create_trigger(
    request: CreateTriggerRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Create a new trigger."""
    try:
        trigger = await trigger_manager.create(
            name=request.name,
            workspace_id=request.workspace_id,
            trigger_type=request.trigger_type,
            config=request.config,
            agent_id=request.agent_id,
            task_template=request.task_template
        )
        return trigger
    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/triggers", response_model=list[Trigger])
async def list_triggers(
    workspace_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """List all triggers for a workspace."""
    try:
        triggers = await trigger_manager.list(workspace_id)
        return triggers
    except Exception as e:
        logger.error(f"Error listing triggers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/triggers/{trigger_id}")
async def delete_trigger(
    trigger_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Delete a trigger."""
    success = await trigger_manager.delete(trigger_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trigger not found")
    
    return {"message": "Trigger deleted successfully"}


@router.post("/triggers/{trigger_id}/fire")
async def fire_trigger(
    trigger_id: str,
    request: FireTriggerRequest = Body(default_factory=FireTriggerRequest),
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Manually fire a trigger."""
    try:
        task_id = await trigger_manager.fire(trigger_id, request.payload)
        return {"task_id": task_id, "message": "Trigger fired successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error firing trigger: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SCHEDULE ENDPOINTS =====

@router.post("/schedules", response_model=ScheduledTask)
async def create_schedule(
    request: CreateScheduleRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Create a new scheduled task."""
    try:
        schedule = await scheduler.create(
            name=request.name,
            workspace_id=request.workspace_id,
            agent_id=request.agent_id,
            task_description=request.task_description,
            cron_expression=request.cron_expression,
            timezone=request.timezone
        )
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules", response_model=list[ScheduledTask])
async def list_schedules(
    workspace_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """List all schedules for a workspace."""
    try:
        schedules = await scheduler.list(workspace_id)
        return schedules
    except Exception as e:
        logger.error(f"Error listing schedules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Delete a schedule."""
    success = await scheduler.delete(schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule deleted successfully"}


@router.post("/schedules/{schedule_id}/run")
async def run_schedule(
    schedule_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Run a scheduled task immediately."""
    try:
        task_id = await scheduler.run_now(schedule_id)
        return {"task_id": task_id, "message": "Schedule executed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{schedule_id}/pause", response_model=ScheduledTask)
async def pause_schedule(
    schedule_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Pause a schedule."""
    schedule = await scheduler.pause(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.post("/schedules/{schedule_id}/resume", response_model=ScheduledTask)
async def resume_schedule(
    schedule_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Resume a schedule."""
    schedule = await scheduler.resume(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


# ===== WEBHOOK ENDPOINTS =====

@router.post("/webhooks", response_model=Webhook)
async def create_webhook(
    request: CreateWebhookRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Create a new webhook."""
    try:
        webhook = await webhook_manager.create(
            workspace_id=request.workspace_id,
            name=request.name,
            trigger_id=request.trigger_id
        )
        return webhook
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/webhooks", response_model=list[Webhook])
async def list_webhooks(
    workspace_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """List all webhooks for a workspace."""
    try:
        webhooks = await webhook_manager.list(workspace_id)
        return webhooks
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Delete a webhook."""
    success = await webhook_manager.delete(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"message": "Webhook deleted successfully"}


@router.post("/webhooks/{webhook_id}/regenerate-secret", response_model=Webhook)
async def regenerate_webhook_secret(
    webhook_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Regenerate webhook secret."""
    webhook = await webhook_manager.regenerate_secret(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.post("/hooks/{url_path}")
async def incoming_webhook(
    url_path: str,
    request: Request
):
    """Handle incoming webhook requests."""
    try:
        # Parse payload
        payload = await request.json()
        headers = dict(request.headers)
        
        # Process webhook
        task_id = await webhook_manager.process(url_path, payload, headers)
        
        return {"task_id": task_id, "message": "Webhook processed successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SUGGESTION ENDPOINTS =====

@router.get("/suggestions", response_model=list[TaskSuggestion])
async def get_suggestions(
    workspace_id: str,
    limit: int = 5,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Get task suggestions for the current user."""
    try:
        suggestions = await suggestion_engine.get_suggestions(
            workspace_id=workspace_id,
            user_id=user_id,
            limit=limit
        )
        return suggestions
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Accept a suggestion and create a task."""
    try:
        task_id = await suggestion_engine.accept(suggestion_id)
        return {"task_id": task_id, "message": "Suggestion accepted, task created"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error accepting suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(
    suggestion_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Dismiss a suggestion."""
    success = await suggestion_engine.dismiss(suggestion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return {"message": "Suggestion dismissed"}


# ===== PATTERN ANALYSIS ENDPOINT =====

@router.get("/patterns")
async def analyze_patterns(
    workspace_id: str,
    user_id: str = Depends(verify_and_get_user_id_from_jwt)
):
    """Analyze user patterns for task suggestions."""
    try:
        analysis = await suggestion_engine.analyze_patterns(workspace_id, user_id)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))
