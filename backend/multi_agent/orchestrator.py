"""
Agent Orchestrator - Central coordinator for all agents

The orchestrator manages the lifecycle of multiple agents, coordinates their work,
and ensures they work together efficiently to accomplish complex tasks.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    id: str
    agent_id: str
    description: str
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentInstance:
    """Represents a running agent instance"""
    id: str
    type: str
    name: str
    status: AgentStatus
    capabilities: List[str]
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Central orchestrator for managing multiple AI agents.
    
    Features:
    - Agent lifecycle management (spawn, pause, resume, stop)
    - Task assignment and dependency management
    - Load balancing across agents
    - Error handling and recovery
    - Performance monitoring
    """

    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._worker_tasks: List[asyncio.Task] = []

    async def start(self, num_workers: int = 3):
        """Start the orchestrator with specified number of workers"""
        if self._running:
            logger.warning("Orchestrator is already running")
            return

        self._running = True
        logger.info(f"Starting orchestrator with {num_workers} workers")

        # Start worker tasks
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._worker_tasks.append(worker)

    async def stop(self):
        """Stop the orchestrator gracefully"""
        if not self._running:
            return

        logger.info("Stopping orchestrator")
        self._running = False

        # Cancel all worker tasks
        for task in self._worker_tasks:
            task.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)
        self._worker_tasks.clear()

    async def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentInstance:
        """Register a new agent with the orchestrator"""
        if agent_id in self.agents:
            raise ValueError(f"Agent {agent_id} is already registered")

        agent = AgentInstance(
            id=agent_id,
            type=agent_type,
            name=name,
            status=AgentStatus.IDLE,
            capabilities=capabilities,
            metadata=metadata or {}
        )

        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id} ({agent_type})")
        return agent

    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.agents[agent_id]
        if agent.current_task:
            logger.warning(f"Agent {agent_id} has active task, cancelling")
            # Cancel current task
            if agent.current_task in self.tasks:
                self.tasks[agent.current_task].status = AgentStatus.ERROR
                self.tasks[agent.current_task].error = "Agent unregistered"

        del self.agents[agent_id]
        logger.info(f"Unregistered agent: {agent_id}")

    async def submit_task(
        self,
        task_id: str,
        agent_id: Optional[str],
        description: str,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentTask:
        """Submit a new task for execution"""
        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")

        task = AgentTask(
            id=task_id,
            agent_id=agent_id or "",
            description=description,
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )

        self.tasks[task_id] = task
        await self.task_queue.put(task)
        logger.info(f"Submitted task: {task_id} (priority: {priority})")
        return task

    async def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get status of a specific task"""
        return self.tasks.get(task_id)

    async def get_agent_status(self, agent_id: str) -> Optional[AgentInstance]:
        """Get status of a specific agent"""
        return self.agents.get(agent_id)

    async def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentInstance]:
        """List all agents, optionally filtered by status"""
        agents = list(self.agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents

    async def list_tasks(self, status: Optional[AgentStatus] = None) -> List[AgentTask]:
        """List all tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    async def pause_agent(self, agent_id: str):
        """Pause an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        self.agents[agent_id].status = AgentStatus.PAUSED
        logger.info(f"Paused agent: {agent_id}")

    async def resume_agent(self, agent_id: str):
        """Resume a paused agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")

        self.agents[agent_id].status = AgentStatus.IDLE
        logger.info(f"Resumed agent: {agent_id}")

    async def _worker(self, worker_id: str):
        """Worker coroutine that processes tasks from the queue"""
        logger.info(f"Worker {worker_id} started")

        while self._running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                # Check if task dependencies are met
                if not await self._check_dependencies(task):
                    # Put task back in queue
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.1)
                    continue

                # Find available agent for task
                agent = await self._find_agent_for_task(task)
                if not agent:
                    # No agent available, put task back
                    await self.task_queue.put(task)
                    await asyncio.sleep(0.5)
                    continue

                # Execute task
                await self._execute_task(agent, task)

            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}", exc_info=True)

        logger.info(f"Worker {worker_id} stopped")

    async def _check_dependencies(self, task: AgentTask) -> bool:
        """Check if task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            dep_task = self.tasks[dep_id]
            if dep_task.status != AgentStatus.COMPLETED:
                return False
        return True

    async def _find_agent_for_task(self, task: AgentTask) -> Optional[AgentInstance]:
        """Find an available agent for the task"""
        # If task has specific agent assigned
        if task.agent_id and task.agent_id in self.agents:
            agent = self.agents[task.agent_id]
            if agent.status == AgentStatus.IDLE:
                return agent
            return None

        # Find any idle agent with required capabilities
        # For now, just find any idle agent
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE:
                return agent

        return None

    async def _execute_task(self, agent: AgentInstance, task: AgentTask):
        """Execute a task on an agent"""
        logger.info(f"Executing task {task.id} on agent {agent.id}")

        # Update statuses
        agent.status = AgentStatus.RUNNING
        agent.current_task = task.id
        agent.last_active = datetime.utcnow()

        task.status = AgentStatus.RUNNING
        task.agent_id = agent.id
        task.started_at = datetime.utcnow()

        try:
            # TODO: Replace with actual agent implementation call
            # Example: result = await agent.execute(task)
            # For now, simulate task execution
            await asyncio.sleep(1.0)

            # Task completed successfully
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = {"success": True, "message": "Task completed"}

            agent.tasks_completed += 1

        except Exception as e:
            # Task failed
            logger.error(f"Task {task.id} failed: {e}", exc_info=True)
            task.status = AgentStatus.ERROR
            task.completed_at = datetime.utcnow()
            task.error = str(e)

            agent.tasks_failed += 1

        finally:
            # Reset agent status
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.last_active = datetime.utcnow()

    async def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total_agents = len(self.agents)
        running_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.RUNNING)
        idle_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.IDLE)

        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == AgentStatus.COMPLETED)
        running_tasks = sum(1 for t in self.tasks.values() if t.status == AgentStatus.RUNNING)
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == AgentStatus.ERROR)

        return {
            "agents": {
                "total": total_agents,
                "running": running_agents,
                "idle": idle_agents,
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "running": running_tasks,
                "failed": failed_tasks,
                "queued": self.task_queue.qsize(),
            },
            "running": self._running,
        }
