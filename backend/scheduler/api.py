"""
FastAPI router for scheduler endpoints.

This module provides REST API endpoints for task scheduling,
background execution, and notification management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .models import (
    CreateScheduleRequest,
    SubmitTaskRequest,
    ScheduledTask,
    TaskStatusInfo,
    TaskStatus,
    TaskListResponse,
    ScheduleListResponse
)
from .task_scheduler import TaskScheduler
from .background_executor import BackgroundExecutor
from .notification_service import NotificationService


# Initialize components
router = APIRouter(prefix="/scheduler", tags=["scheduler"])
task_scheduler = TaskScheduler()
background_executor = BackgroundExecutor()
notification_service = NotificationService()


# Scheduler Endpoints
@router.post("/schedule", response_model=dict)
async def create_schedule(request: CreateScheduleRequest):
    """
    Create a scheduled task.
    
    Schedule a task to run at specific times using cron expressions.
    """
    try:
        schedule_id = await task_scheduler.schedule(
            name=request.name,
            cron_expression=request.cron_expression,
            task_definition=request.task_definition,
            description=request.description,
            timezone=request.timezone,
            max_retries=request.max_retries,
            enabled=request.enabled
        )
        
        return {
            "schedule_id": schedule_id,
            "message": "Schedule created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/schedule/{schedule_id}", response_model=dict)
async def cancel_schedule(schedule_id: str):
    """
    Cancel a scheduled task.
    
    Remove a schedule from the system.
    """
    success = await task_scheduler.cancel(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule cancelled successfully"}


@router.post("/schedule/{schedule_id}/pause", response_model=dict)
async def pause_schedule(schedule_id: str):
    """
    Pause a scheduled task.
    
    Temporarily stop a schedule from executing.
    """
    success = await task_scheduler.pause(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {"message": "Schedule paused successfully"}


@router.post("/schedule/{schedule_id}/resume", response_model=dict)
async def resume_schedule(schedule_id: str):
    """
    Resume a paused scheduled task.
    
    Resume execution of a paused schedule.
    """
    success = await task_scheduler.resume(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found or not paused")
    
    return {"message": "Schedule resumed successfully"}


@router.get("/schedules", response_model=ScheduleListResponse)
async def list_schedules(
    enabled_only: bool = Query(False, description="Only return enabled schedules"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all scheduled tasks.
    
    Get a paginated list of all schedules with optional filtering.
    """
    schedules = await task_scheduler.list_schedules(enabled_only=enabled_only)
    
    # Calculate pagination
    total = len(schedules)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = schedules[start:end]
    
    return ScheduleListResponse(
        schedules=paginated,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/schedule/{schedule_id}", response_model=ScheduledTask)
async def get_schedule(schedule_id: str):
    """
    Get a specific schedule.
    
    Retrieve details about a scheduled task.
    """
    schedule = await task_scheduler.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule


@router.get("/schedule/{schedule_id}/next-run", response_model=dict)
async def get_next_run(schedule_id: str):
    """
    Get the next run time for a schedule.
    
    Returns when the schedule will next execute.
    """
    next_run = await task_scheduler.get_next_run(schedule_id)
    
    if not next_run:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {
        "schedule_id": schedule_id,
        "next_run": next_run.isoformat()
    }


# Background Task Endpoints
@router.post("/tasks", response_model=dict)
async def submit_task(request: SubmitTaskRequest):
    """
    Submit a background task.
    
    Create a new background task for asynchronous execution.
    """
    try:
        task_id = await background_executor.submit(
            name=request.name,
            task_type=request.task_type,
            parameters=request.parameters,
            description=request.description,
            priority=request.priority,
            max_retries=request.max_retries,
            timeout_seconds=request.timeout_seconds,
            dependencies=request.dependencies
        )
        
        return {
            "task_id": task_id,
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusInfo)
async def get_task_status(task_id: str):
    """
    Get task status.
    
    Retrieve current status and progress of a background task.
    """
    status = await background_executor.get_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return status


@router.post("/tasks/{task_id}/cancel", response_model=dict)
async def cancel_task(task_id: str):
    """
    Cancel a task.
    
    Cancel a pending or paused task.
    """
    success = await background_executor.cancel(task_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Task not found or cannot be cancelled"
        )
    
    return {"message": "Task cancelled successfully"}


@router.post("/tasks/{task_id}/pause", response_model=dict)
async def pause_task(task_id: str):
    """
    Pause a task.
    
    Pause a pending task.
    """
    success = await background_executor.pause(task_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Task not found or cannot be paused"
        )
    
    return {"message": "Task paused successfully"}


@router.post("/tasks/{task_id}/resume", response_model=dict)
async def resume_task(task_id: str):
    """
    Resume a task.
    
    Resume a paused task.
    """
    success = await background_executor.resume(task_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Task not found or not paused"
        )
    
    return {"message": "Task resumed successfully"}


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List all tasks.
    
    Get a paginated list of all background tasks with optional status filtering.
    """
    offset = (page - 1) * page_size
    tasks = await background_executor.list_tasks(
        status=status,
        limit=page_size,
        offset=offset
    )
    
    # Get total count
    all_tasks = await background_executor.list_tasks(status=status, limit=10000)
    total = len(all_tasks)
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size
    )


# System Status Endpoints
@router.get("/stats", response_model=dict)
async def get_stats():
    """
    Get scheduler and executor statistics.
    
    Returns current system statistics including queue sizes and task counts.
    """
    return {
        "scheduler": task_scheduler.get_stats(),
        "executor": background_executor.get_stats()
    }


@router.post("/start", response_model=dict)
async def start_scheduler():
    """
    Start the scheduler and executor.
    
    Initialize and start background workers.
    """
    await task_scheduler.start()
    await background_executor.start()
    
    return {"message": "Scheduler and executor started successfully"}


@router.post("/stop", response_model=dict)
async def stop_scheduler():
    """
    Stop the scheduler and executor.
    
    Gracefully shutdown background workers.
    """
    await task_scheduler.stop()
    await background_executor.stop()
    
    return {"message": "Scheduler and executor stopped successfully"}


# Initialize on startup
async def initialize():
    """Initialize the scheduler system."""
    await task_scheduler.start()
    await background_executor.start()


async def cleanup():
    """Cleanup on shutdown."""
    await task_scheduler.stop()
    await background_executor.stop()
