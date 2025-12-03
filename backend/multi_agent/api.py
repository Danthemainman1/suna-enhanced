"""
Multi-Agent API Endpoints

FastAPI routes for interacting with the multi-agent orchestration system.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .orchestrator import AgentOrchestrator, AgentStatus
from .agent_registry import AgentRegistry, AgentCategory
from .task_decomposer import TaskDecomposer
from .agent_spawner import AgentSpawner
from .communication_bus import CommunicationBus
from .consensus_engine import ConsensusEngine, VotingStrategy, AgentOpinion
from .load_balancer import LoadBalancer, LoadBalancingStrategy

# Initialize components (in production, these would be singletons)
orchestrator = AgentOrchestrator()
registry = AgentRegistry()
decomposer = TaskDecomposer()
spawner = AgentSpawner(max_agents=20)
bus = CommunicationBus()
consensus = ConsensusEngine()
load_balancer = LoadBalancer()

router = APIRouter(prefix="/api/multi-agent", tags=["Multi-Agent"])


# Request/Response Models
class RegisterAgentRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent")
    name: str = Field(..., description="Human-readable agent name")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    metadata: Optional[Dict[str, Any]] = None


class SubmitTaskRequest(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    agent_id: Optional[str] = Field(None, description="Specific agent to assign to")
    description: str = Field(..., description="Task description")
    priority: int = Field(0, description="Task priority (higher = more important)")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    metadata: Optional[Dict[str, Any]] = None


class DecomposeTaskRequest(BaseModel):
    task_id: str = Field(..., description="Task identifier")
    task_description: str = Field(..., description="Task to decompose")
    context: Optional[Dict[str, Any]] = None


class ConsensusRequest(BaseModel):
    opinions: List[Dict[str, Any]] = Field(..., description="Agent opinions")
    strategy: str = Field("weighted", description="Voting strategy")
    threshold: float = Field(0.5, description="Threshold for threshold-based voting")


class AgentResponse(BaseModel):
    id: str
    type: str
    name: str
    status: str
    capabilities: List[str]
    current_task: Optional[str]
    tasks_completed: int
    tasks_failed: int
    created_at: datetime
    last_active: datetime


class TaskResponse(BaseModel):
    id: str
    agent_id: str
    description: str
    priority: int
    status: str
    dependencies: List[str]
    result: Optional[Any]
    error: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class OrchestratorStatsResponse(BaseModel):
    agents: Dict[str, int]
    tasks: Dict[str, int]
    running: bool


# Orchestrator Endpoints

@router.post("/orchestrator/start")
async def start_orchestrator(num_workers: int = 3):
    """Start the agent orchestrator"""
    await orchestrator.start(num_workers=num_workers)
    return {"status": "started", "workers": num_workers}


@router.post("/orchestrator/stop")
async def stop_orchestrator():
    """Stop the agent orchestrator"""
    await orchestrator.stop()
    return {"status": "stopped"}


@router.get("/orchestrator/stats", response_model=OrchestratorStatsResponse)
async def get_orchestrator_stats():
    """Get orchestrator statistics"""
    stats = await orchestrator.get_stats()
    return stats


@router.post("/agents/register", response_model=AgentResponse)
async def register_agent(request: RegisterAgentRequest):
    """Register a new agent"""
    try:
        agent = await orchestrator.register_agent(
            agent_id=request.agent_id,
            agent_type=request.agent_type,
            name=request.name,
            capabilities=request.capabilities,
            metadata=request.metadata,
        )
        return AgentResponse(
            id=agent.id,
            type=agent.type,
            name=agent.name,
            status=agent.status.value,
            capabilities=agent.capabilities,
            current_task=agent.current_task,
            tasks_completed=agent.tasks_completed,
            tasks_failed=agent.tasks_failed,
            created_at=agent.created_at,
            last_active=agent.last_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/agents/{agent_id}")
async def unregister_agent(agent_id: str):
    """Unregister an agent"""
    try:
        await orchestrator.unregister_agent(agent_id)
        return {"status": "unregistered", "agent_id": agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(status: Optional[str] = None):
    """List all agents"""
    agent_status = AgentStatus(status) if status else None
    agents = await orchestrator.list_agents(status=agent_status)
    return [
        AgentResponse(
            id=agent.id,
            type=agent.type,
            name=agent.name,
            status=agent.status.value,
            capabilities=agent.capabilities,
            current_task=agent.current_task,
            tasks_completed=agent.tasks_completed,
            tasks_failed=agent.tasks_failed,
            created_at=agent.created_at,
            last_active=agent.last_active,
        )
        for agent in agents
    ]


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    agent = await orchestrator.get_agent_status(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(
        id=agent.id,
        type=agent.type,
        name=agent.name,
        status=agent.status.value,
        capabilities=agent.capabilities,
        current_task=agent.current_task,
        tasks_completed=agent.tasks_completed,
        tasks_failed=agent.tasks_failed,
        created_at=agent.created_at,
        last_active=agent.last_active,
    )


@router.post("/agents/{agent_id}/pause")
async def pause_agent(agent_id: str):
    """Pause an agent"""
    try:
        await orchestrator.pause_agent(agent_id)
        return {"status": "paused", "agent_id": agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/agents/{agent_id}/resume")
async def resume_agent(agent_id: str):
    """Resume a paused agent"""
    try:
        await orchestrator.resume_agent(agent_id)
        return {"status": "resumed", "agent_id": agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Task Endpoints

@router.post("/tasks/submit", response_model=TaskResponse)
async def submit_task(request: SubmitTaskRequest):
    """Submit a new task"""
    try:
        task = await orchestrator.submit_task(
            task_id=request.task_id,
            agent_id=request.agent_id,
            description=request.description,
            priority=request.priority,
            dependencies=request.dependencies,
            metadata=request.metadata,
        )
        return TaskResponse(
            id=task.id,
            agent_id=task.agent_id,
            description=task.description,
            priority=task.priority,
            status=task.status.value,
            dependencies=task.dependencies,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(status: Optional[str] = None):
    """List all tasks"""
    task_status = AgentStatus(status) if status else None
    tasks = await orchestrator.list_tasks(status=task_status)
    return [
        TaskResponse(
            id=task.id,
            agent_id=task.agent_id,
            description=task.description,
            priority=task.priority,
            status=task.status.value,
            dependencies=task.dependencies,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )
        for task in tasks
    ]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    task = await orchestrator.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        agent_id=task.agent_id,
        description=task.description,
        priority=task.priority,
        status=task.status.value,
        dependencies=task.dependencies,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
    )


@router.post("/tasks/decompose")
async def decompose_task(request: DecomposeTaskRequest):
    """Decompose a complex task into subtasks"""
    plan = await decomposer.decompose(
        task_id=request.task_id,
        task_description=request.task_description,
        context=request.context,
    )
    return {
        "task_id": plan.task_id,
        "original_task": plan.original_task,
        "execution_strategy": plan.execution_strategy,
        "total_estimated_duration": plan.total_estimated_duration,
        "subtasks": [
            {
                "id": st.id,
                "description": st.description,
                "agent_type": st.agent_type,
                "priority": st.priority,
                "dependencies": st.dependencies,
                "estimated_duration": st.estimated_duration,
            }
            for st in plan.subtasks
        ],
    }


# Registry Endpoints

@router.get("/registry/agent-types")
async def list_agent_types(category: Optional[str] = None):
    """List available agent types"""
    cat = AgentCategory(category) if category else None
    agent_types = registry.list_agent_types(category=cat)
    return [
        {
            "id": at.id,
            "name": at.name,
            "description": at.description,
            "category": at.category.value,
            "capabilities": [
                {"id": c.id, "name": c.name, "description": c.description}
                for c in at.capabilities
            ],
            "version": at.version,
            "author": at.author,
            "tags": at.tags,
        }
        for at in agent_types
    ]


@router.get("/registry/capabilities")
async def list_capabilities(category: Optional[str] = None):
    """List available capabilities"""
    cat = AgentCategory(category) if category else None
    capabilities = registry.list_capabilities(category=cat)
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "category": c.category.value,
            "required_tools": c.required_tools,
            "optional_tools": c.optional_tools,
        }
        for c in capabilities
    ]


# Consensus Endpoints

@router.post("/consensus/vote")
async def vote_for_consensus(request: ConsensusRequest):
    """Reach consensus on a decision"""
    try:
        strategy = VotingStrategy(request.strategy)
        
        # Convert dict opinions to AgentOpinion objects
        opinions = [
            AgentOpinion(
                agent_id=op["agent_id"],
                decision=op["decision"],
                confidence=op["confidence"],
                reasoning=op.get("reasoning", ""),
                weight=op.get("weight", 1.0),
            )
            for op in request.opinions
        ]
        
        result = await consensus.reach_consensus(
            opinions=opinions,
            strategy=strategy,
            threshold=request.threshold,
        )
        
        return {
            "decision": result.decision,
            "confidence": result.confidence,
            "participating_agents": result.participating_agents,
            "voting_strategy": result.voting_strategy.value,
            "metadata": result.metadata,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Load Balancer Endpoints

@router.get("/load-balancer/stats")
async def get_load_balancer_stats():
    """Get load balancer statistics"""
    return load_balancer.get_cluster_stats()


# Communication Bus Endpoints

@router.post("/communication/start")
async def start_communication_bus():
    """Start the communication bus"""
    await bus.start()
    return {"status": "started"}


@router.post("/communication/stop")
async def stop_communication_bus():
    """Stop the communication bus"""
    await bus.stop()
    return {"status": "stopped"}


@router.get("/communication/stats")
async def get_communication_stats():
    """Get communication bus statistics"""
    return bus.get_stats()


@router.get("/communication/history")
async def get_message_history(topic: Optional[str] = None, limit: int = 100):
    """Get message history"""
    messages = bus.get_message_history(topic=topic, limit=limit)
    return [
        {
            "id": msg.id,
            "from_agent": msg.from_agent,
            "to_agent": msg.to_agent,
            "topic": msg.topic,
            "payload": msg.payload,
            "timestamp": msg.timestamp,
        }
        for msg in messages
    ]


# Health Check

@router.get("/health")
async def health_check():
    """Check health of multi-agent system"""
    return {
        "status": "healthy",
        "orchestrator_running": orchestrator._running,
        "communication_bus_running": bus._running,
        "timestamp": datetime.utcnow(),
    }
