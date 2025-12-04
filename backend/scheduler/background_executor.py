"""
Background task execution system.

This module provides persistent task queue with worker pool management,
retry logic, and status tracking that survives restarts.
"""

import uuid
import asyncio
import time
from typing import Optional, Callable, Any
from datetime import datetime
from collections import deque
from .models import (
    BackgroundTask,
    TaskStatus,
    TaskStatusInfo,
    TaskResult
)


class BackgroundExecutor:
    """
    Background task execution with persistent queue.
    
    Manages a pool of workers to execute tasks asynchronously,
    with retry logic, exponential backoff, and status tracking.
    """
    
    def __init__(self, num_workers: int = 4, max_queue_size: int = 1000):
        """
        Initialize the background executor.
        
        Args:
            num_workers: Number of worker tasks
            max_queue_size: Maximum queue size
        """
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        
        # Task storage
        self._tasks: dict[str, BackgroundTask] = {}
        self._task_status: dict[str, TaskStatusInfo] = {}
        self._task_results: dict[str, TaskResult] = {}
        
        # Queue management
        self._pending_queue: deque = deque()
        self._running_tasks: set[str] = set()
        
        # Worker management
        self._workers: list[asyncio.Task] = []
        self._running = False
        
        # Task executors (registered by task type)
        self._executors: dict[str, Callable] = {}
    
    async def start(self):
        """Start the executor and worker pool."""
        if self._running:
            return
        
        self._running = True
        
        # Start worker tasks
        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
    
    async def stop(self):
        """Stop the executor and workers."""
        self._running = False
        
        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
    
    async def submit(
        self,
        name: str,
        task_type: str,
        parameters: Optional[dict] = None,
        description: Optional[str] = None,
        priority: int = 5,
        max_retries: int = 3,
        timeout_seconds: Optional[int] = None,
        dependencies: Optional[list[str]] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Submit a background task for execution.
        
        Args:
            name: Task name
            task_type: Type of task
            parameters: Task parameters
            description: Task description
            priority: Priority (1=lowest, 10=highest)
            max_retries: Maximum retry attempts
            timeout_seconds: Task timeout
            dependencies: Task IDs this depends on
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        if len(self._pending_queue) >= self.max_queue_size:
            raise RuntimeError("Task queue is full")
        
        task_id = str(uuid.uuid4())
        
        task = BackgroundTask(
            task_id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            parameters=parameters or {},
            priority=priority,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self._tasks[task_id] = task
        
        # Create initial status
        status = TaskStatusInfo(
            task_id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            progress=0.0,
            created_at=task.created_at,
            updated_at=task.created_at
        )
        self._task_status[task_id] = status
        
        # Add to queue (sorted by priority)
        self._enqueue_task(task_id)
        
        return task_id
    
    def _enqueue_task(self, task_id: str):
        """Add task to queue based on priority."""
        task = self._tasks[task_id]
        
        # Find insertion point based on priority
        inserted = False
        for i, queued_id in enumerate(self._pending_queue):
            queued_task = self._tasks[queued_id]
            if task.priority > queued_task.priority:
                self._pending_queue.insert(i, task_id)
                inserted = True
                break
        
        if not inserted:
            self._pending_queue.append(task_id)
    
    async def get_status(self, task_id: str) -> Optional[TaskStatusInfo]:
        """
        Get current status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            TaskStatusInfo if found, None otherwise
        """
        return self._task_status.get(task_id)
    
    async def cancel(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        if task_id not in self._task_status:
            return False
        
        status = self._task_status[task_id]
        
        # Can only cancel pending or paused tasks
        if status.status in [TaskStatus.PENDING, TaskStatus.PAUSED]:
            status.status = TaskStatus.CANCELLED
            status.updated_at = datetime.utcnow()
            
            # Remove from queue if present
            if task_id in self._pending_queue:
                self._pending_queue.remove(task_id)
            
            return True
        
        return False
    
    async def pause(self, task_id: str) -> bool:
        """
        Pause a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if paused, False if not found or already completed
        """
        if task_id not in self._task_status:
            return False
        
        status = self._task_status[task_id]
        
        # Can only pause pending tasks
        if status.status == TaskStatus.PENDING:
            status.status = TaskStatus.PAUSED
            status.updated_at = datetime.utcnow()
            
            # Remove from queue
            if task_id in self._pending_queue:
                self._pending_queue.remove(task_id)
            
            return True
        
        return False
    
    async def resume(self, task_id: str) -> bool:
        """
        Resume a paused task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if resumed, False if not found or not paused
        """
        if task_id not in self._task_status:
            return False
        
        status = self._task_status[task_id]
        
        # Can only resume paused tasks
        if status.status == TaskStatus.PAUSED:
            status.status = TaskStatus.PENDING
            status.updated_at = datetime.utcnow()
            
            # Re-add to queue
            self._enqueue_task(task_id)
            
            return True
        
        return False
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[TaskStatusInfo]:
        """
        List tasks with optional status filter.
        
        Args:
            status: Optional status filter
            limit: Maximum number to return
            offset: Offset for pagination
            
        Returns:
            List of task status info
        """
        tasks = list(self._task_status.values())
        
        # Filter by status if provided
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply pagination
        return tasks[offset:offset + limit]
    
    def register_executor(
        self,
        task_type: str,
        executor: Callable[[dict], Any]
    ):
        """
        Register an executor function for a task type.
        
        Args:
            task_type: Type of task
            executor: Async function to execute tasks of this type
        """
        self._executors[task_type] = executor
    
    async def _worker(self, worker_id: int):
        """Worker task that processes the queue."""
        while self._running:
            try:
                # Get next task from queue
                task_id = await self._get_next_task()
                
                if task_id is None:
                    # No tasks available, wait a bit
                    await asyncio.sleep(1)
                    continue
                
                # Execute the task
                await self._execute_task(task_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def _get_next_task(self) -> Optional[str]:
        """Get the next task from queue that's ready to execute."""
        if not self._pending_queue:
            return None
        
        # Find first task with no pending dependencies
        for i, task_id in enumerate(self._pending_queue):
            task = self._tasks[task_id]
            
            # Check dependencies
            if await self._dependencies_satisfied(task):
                self._pending_queue.remove(task_id)
                self._running_tasks.add(task_id)
                return task_id
        
        return None
    
    async def _dependencies_satisfied(self, task: BackgroundTask) -> bool:
        """Check if all task dependencies are completed successfully."""
        for dep_id in task.dependencies:
            if dep_id not in self._task_status:
                return False
            
            dep_status = self._task_status[dep_id]
            if dep_status.status != TaskStatus.COMPLETED:
                return False
            
            # Check if dependency succeeded
            if dep_status.result and not dep_status.result.success:
                return False
        
        return True
    
    async def _execute_task(self, task_id: str):
        """Execute a task."""
        task = self._tasks[task_id]
        status = self._task_status[task_id]
        
        # Update status to running
        status.status = TaskStatus.RUNNING
        status.started_at = datetime.utcnow()
        status.updated_at = datetime.utcnow()
        
        start_time = time.time()
        
        try:
            # Get executor for task type
            executor = self._executors.get(task.task_type)
            
            if executor is None:
                raise RuntimeError(f"No executor registered for task type: {task.task_type}")
            
            # Execute with timeout if specified
            if task.timeout_seconds:
                result = await asyncio.wait_for(
                    executor(task.parameters),
                    timeout=task.timeout_seconds
                )
            else:
                result = await executor(task.parameters)
            
            # Task succeeded
            duration = time.time() - start_time
            
            task_result = TaskResult(
                task_id=task_id,
                success=True,
                result=result,
                started_at=status.started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=duration,
                retry_count=task.retry_count
            )
            
            status.status = TaskStatus.COMPLETED
            status.result = task_result
            status.progress = 1.0
            status.updated_at = datetime.utcnow()
            
            self._task_results[task_id] = task_result
            
        except asyncio.TimeoutError:
            await self._handle_task_failure(
                task,
                status,
                start_time,
                "Task timed out"
            )
        except Exception as e:
            await self._handle_task_failure(
                task,
                status,
                start_time,
                str(e)
            )
        finally:
            self._running_tasks.discard(task_id)
    
    async def _handle_task_failure(
        self,
        task: BackgroundTask,
        status: TaskStatusInfo,
        start_time: float,
        error: str
    ):
        """Handle task failure with retry logic."""
        task.retry_count += 1
        
        # Check if we should retry
        if task.retry_count < task.max_retries:
            # Exponential backoff
            delay = min(300, 2 ** task.retry_count * 10)  # Max 5 minutes
            await asyncio.sleep(delay)
            
            # Re-queue the task
            status.status = TaskStatus.PENDING
            status.updated_at = datetime.utcnow()
            self._enqueue_task(task.task_id)
        else:
            # Max retries reached, mark as failed
            duration = time.time() - start_time
            
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=error,
                started_at=status.started_at,
                completed_at=datetime.utcnow(),
                duration_seconds=duration,
                retry_count=task.retry_count
            )
            
            status.status = TaskStatus.FAILED
            status.result = task_result
            status.updated_at = datetime.utcnow()
            
            self._task_results[task.task_id] = task_result
    
    def get_stats(self) -> dict:
        """
        Get executor statistics.
        
        Returns:
            Dictionary with statistics
        """
        by_status = {}
        for status_info in self._task_status.values():
            status = status_info.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'running': self._running,
            'num_workers': self.num_workers,
            'queue_size': len(self._pending_queue),
            'running_tasks': len(self._running_tasks),
            'total_tasks': len(self._tasks),
            'tasks_by_status': by_status,
            'registered_executors': list(self._executors.keys())
        }
