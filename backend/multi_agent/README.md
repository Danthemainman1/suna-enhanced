# Suna Ultra Multi-Agent Orchestration System

A sophisticated multi-agent orchestration framework that enables multiple AI agents to work together, communicate, and coordinate on complex tasks.

## 🎯 Overview

The Multi-Agent Orchestration System is the core differentiator of Suna Ultra. Unlike traditional single-agent systems (like Manus AI, ChatGPT, or Claude), Suna Ultra can spawn multiple specialized agents that collaborate to solve complex problems more efficiently.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                      │
│         (Central coordinator and task manager)           │
└─────────────────────┬───────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐   ┌───▼────┐  ┌───▼────┐
    │ Agent  │   │ Agent  │  │ Agent  │
    │ Registry│   │Spawner │  │  Load  │
    │        │   │        │  │Balancer│
    └────────┘   └────────┘  └────────┘
         │            │            │
    ┌────▼────────────▼────────────▼────┐
    │      Communication Bus             │
    │    (Inter-agent messaging)         │
    └────────────────┬───────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
    │  Task  │  │Consensus│  │Specialized│
    │Decomposer│ │ Engine │  │  Agents  │
    └────────┘  └────────┘  └──────────┘
```

## 📦 Components

### 1. Agent Orchestrator (`orchestrator.py`)

Central coordinator that manages the lifecycle of all agents and coordinates their work.

**Features:**
- Agent lifecycle management (spawn, pause, resume, stop)
- Task queue and assignment
- Dependency management
- Error handling and recovery
- Performance monitoring

**Example Usage:**

```python
from multi_agent import AgentOrchestrator

# Initialize orchestrator
orchestrator = AgentOrchestrator()
await orchestrator.start(num_workers=3)

# Register an agent
agent = await orchestrator.register_agent(
    agent_id="research_1",
    agent_type="research_agent",
    name="Research Agent Alpha",
    capabilities=["web_research", "data_synthesis"]
)

# Submit a task
task = await orchestrator.submit_task(
    task_id="task_001",
    agent_id="research_1",
    description="Research AI market trends for 2025",
    priority=5
)

# Get statistics
stats = await orchestrator.get_stats()
print(f"Active agents: {stats['agents']['running']}")
print(f"Completed tasks: {stats['tasks']['completed']}")
```

### 2. Agent Registry (`agent_registry.py`)

Maintains a catalog of available agent types and their capabilities.

**Features:**
- Agent type registration and discovery
- Capability-based agent selection
- Version management
- Configuration validation

**Example Usage:**

```python
from multi_agent import AgentRegistry
from multi_agent.agent_registry import AgentCategory

registry = AgentRegistry()

# List all research agents
research_agents = registry.list_agent_types(category=AgentCategory.RESEARCH)

# Find agents with specific capability
agents = registry.find_agents_by_capability("web_research")

# Get agent details
agent_type = registry.get_agent_type("research_agent")
print(f"Agent: {agent_type.name}")
print(f"Capabilities: {[c.name for c in agent_type.capabilities]}")
```

### 3. Task Decomposer (`task_decomposer.py`)

Breaks down complex tasks into smaller, manageable subtasks.

**Features:**
- Pattern-based task decomposition
- Dependency calculation
- Execution strategy optimization
- Duration estimation

**Example Usage:**

```python
from multi_agent import TaskDecomposer

decomposer = TaskDecomposer()

# Decompose a complex task
plan = await decomposer.decompose(
    task_id="complex_task_1",
    task_description="Research competitors and create a detailed report",
)

print(f"Strategy: {plan.execution_strategy}")
print(f"Subtasks: {len(plan.subtasks)}")
for subtask in plan.subtasks:
    print(f"  - {subtask.description} ({subtask.agent_type})")
```

### 4. Agent Spawner (`agent_spawner.py`)

Dynamically creates and manages agent instances on-demand.

**Features:**
- On-demand agent creation
- Agent pool management
- Resource allocation
- Automatic scaling

**Example Usage:**

```python
from multi_agent import AgentSpawner

spawner = AgentSpawner(max_agents=10)

# Spawn a new agent
agent_id = await spawner.spawn_agent(
    agent_type="research_agent",
    config={"model": "gpt-4", "temperature": 0.7}
)

# Get pool statistics
stats = await spawner.get_agent_pool_stats()
print(f"Active agents: {stats['active_agents']}/{stats['max_agents']}")
print(f"Utilization: {stats['utilization']*100:.1f}%")
```

### 5. Communication Bus (`communication_bus.py`)

Pub/Sub messaging system for inter-agent communication.

**Features:**
- Topic-based messaging
- Broadcast and direct messaging
- Message queuing
- Message history

**Example Usage:**

```python
from multi_agent import CommunicationBus

bus = CommunicationBus()
await bus.start()

# Subscribe to a topic
async def handle_message(message):
    print(f"Received: {message.payload}")

bus.subscribe("agent.results", handle_message)

# Publish a message
await bus.publish(
    from_agent="research_1",
    topic="agent.results",
    payload={"status": "completed", "data": {...}}
)

# Get stats
stats = bus.get_stats()
print(f"Total messages: {stats['total_messages']}")
```

### 6. Consensus Engine (`consensus_engine.py`)

Facilitates multi-agent decision making through voting and consensus.

**Features:**
- Multiple voting strategies (majority, weighted, unanimous, threshold)
- Weighted voting based on agent expertise
- Conflict resolution
- Confidence scoring

**Example Usage:**

```python
from multi_agent import ConsensusEngine
from multi_agent.consensus_engine import AgentOpinion, VotingStrategy

engine = ConsensusEngine()

# Set agent weights
engine.set_agent_weight("expert_agent", 1.0)
engine.set_agent_weight("junior_agent", 0.5)

# Collect opinions
opinions = [
    AgentOpinion(
        agent_id="expert_agent",
        decision="Option A",
        confidence=0.9,
        reasoning="Based on data analysis..."
    ),
    AgentOpinion(
        agent_id="junior_agent",
        decision="Option B",
        confidence=0.6,
        reasoning="Alternative approach..."
    ),
]

# Reach consensus
result = await engine.reach_consensus(
    opinions=opinions,
    strategy=VotingStrategy.WEIGHTED
)

print(f"Decision: {result.decision}")
print(f"Confidence: {result.confidence:.2f}")
```

### 7. Load Balancer (`load_balancer.py`)

Distributes tasks across agents based on load and capabilities.

**Features:**
- Multiple load balancing strategies
- Real-time load monitoring
- Capability-based routing
- Performance-based distribution

**Example Usage:**

```python
from multi_agent import LoadBalancer
from multi_agent.load_balancer import LoadBalancingStrategy

balancer = LoadBalancer(strategy=LoadBalancingStrategy.LEAST_LOADED)

# Update agent load
balancer.update_agent_load(
    agent_id="agent_1",
    active_tasks=2,
    total_capacity=5,
    cpu_usage=0.45,
    memory_usage=0.60,
    success_rate=0.95
)

# Select agent for task
selected_agent = await balancer.select_agent(
    available_agents=["agent_1", "agent_2", "agent_3"]
)

# Get cluster stats
stats = balancer.get_cluster_stats()
print(f"Average utilization: {stats['avg_utilization']*100:.1f}%")
```

## 🚀 Quick Start

### Complete Example: Multi-Agent Workflow

```python
import asyncio
from multi_agent import (
    AgentOrchestrator,
    AgentRegistry,
    TaskDecomposer,
    CommunicationBus,
)

async def main():
    # Initialize components
    orchestrator = AgentOrchestrator()
    registry = AgentRegistry()
    decomposer = TaskDecomposer()
    bus = CommunicationBus()
    
    # Start systems
    await orchestrator.start(num_workers=3)
    await bus.start()
    
    # Register agents
    for agent_type in ["research_agent", "writer_agent", "critic_agent"]:
        agent_info = registry.get_agent_type(agent_type)
        await orchestrator.register_agent(
            agent_id=f"{agent_type}_1",
            agent_type=agent_type,
            name=agent_info.name,
            capabilities=[c.id for c in agent_info.capabilities]
        )
    
    # Decompose complex task
    plan = await decomposer.decompose(
        task_id="market_analysis",
        task_description="Research AI market and create comprehensive report"
    )
    
    # Submit subtasks
    for subtask in plan.subtasks:
        await orchestrator.submit_task(
            task_id=subtask.id,
            agent_id=None,  # Let orchestrator assign
            description=subtask.description,
            priority=subtask.priority,
            dependencies=subtask.dependencies
        )
    
    # Monitor progress
    while True:
        stats = await orchestrator.get_stats()
        if stats['tasks']['running'] == 0 and stats['tasks']['queued'] == 0:
            break
        await asyncio.sleep(1)
    
    print(f"✅ Completed {stats['tasks']['completed']} tasks")
    
    # Cleanup
    await bus.stop()
    await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎓 Advanced Topics

### Custom Agent Types

Register your own specialized agent types:

```python
from multi_agent.agent_registry import AgentCapability, AgentCategory

# Define capabilities
custom_capabilities = [
    AgentCapability(
        id="custom_analysis",
        name="Custom Analysis",
        description="Perform domain-specific analysis",
        category=AgentCategory.DATA,
        required_tools=["custom_analyzer"]
    )
]

# Register agent type
registry.register_agent_type(
    agent_id="custom_agent",
    name="Custom Agent",
    description="Specialized agent for custom tasks",
    category=AgentCategory.DATA,
    capabilities=custom_capabilities
)
```

### Error Handling and Recovery

```python
try:
    task = await orchestrator.submit_task(...)
except Exception as e:
    logger.error(f"Task submission failed: {e}")
    # Retry logic here

# Monitor task status
task_status = await orchestrator.get_task_status(task.id)
if task_status.status == AgentStatus.ERROR:
    print(f"Task failed: {task_status.error}")
```

### Performance Monitoring

```python
# Get detailed statistics
stats = await orchestrator.get_stats()

# Agent performance
agents = await orchestrator.list_agents()
for agent in agents:
    success_rate = agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)
    print(f"{agent.name}: {success_rate*100:.1f}% success rate")

# Load balancing stats
cluster_stats = balancer.get_cluster_stats()
print(f"Cluster utilization: {cluster_stats['avg_utilization']*100:.1f}%")
```

## 🔧 Configuration

Environment variables:

```bash
# Multi-agent settings
MAX_AGENTS=10
WORKER_THREADS=3
TASK_QUEUE_SIZE=1000
MESSAGE_HISTORY_SIZE=10000

# Load balancing
LOAD_BALANCING_STRATEGY=least_loaded
AGENT_CAPACITY=5

# Communication
MESSAGE_BUS_BUFFER_SIZE=1000
```

## 📚 API Reference

See individual module docstrings for detailed API documentation.

## 🧪 Testing

Run tests:

```bash
pytest backend/multi_agent/tests/
```

## 🤝 Contributing

Contributions to the multi-agent system are welcome! Please follow the contribution guidelines.

## 📄 License

Apache License 2.0 - See LICENSE file for details.

---

**Suna Ultra** - The Future of Multi-Agent AI Systems
