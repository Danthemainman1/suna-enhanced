"""
Load Balancer - Distribute work across agents

Intelligently distributes tasks across available agents based on load,
capabilities, and performance metrics.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    CAPABILITY_BASED = "capability_based"


@dataclass
class AgentLoad:
    """Represents the current load of an agent"""
    agent_id: str
    active_tasks: int
    total_capacity: int
    cpu_usage: float  # 0.0 to 1.0
    memory_usage: float  # 0.0 to 1.0
    success_rate: float  # 0.0 to 1.0
    avg_task_duration: float  # in seconds
    last_updated: datetime = datetime.utcnow()


class LoadBalancer:
    """
    Distribute tasks across agents efficiently.
    
    Features:
    - Multiple load balancing strategies
    - Real-time load monitoring
    - Capability-based routing
    - Performance-based distribution
    """

    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.strategy = strategy
        self.agent_loads: Dict[str, AgentLoad] = {}
        self._round_robin_index = 0

    def update_agent_load(
        self,
        agent_id: str,
        active_tasks: int,
        total_capacity: int,
        cpu_usage: float = 0.0,
        memory_usage: float = 0.0,
        success_rate: float = 1.0,
        avg_task_duration: float = 60.0,
    ):
        """Update load information for an agent"""
        self.agent_loads[agent_id] = AgentLoad(
            agent_id=agent_id,
            active_tasks=active_tasks,
            total_capacity=total_capacity,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            success_rate=success_rate,
            avg_task_duration=avg_task_duration,
        )

    def remove_agent(self, agent_id: str):
        """Remove an agent from load balancing"""
        if agent_id in self.agent_loads:
            del self.agent_loads[agent_id]

    async def select_agent(
        self,
        available_agents: List[str],
        task_requirements: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Select an agent for a task based on the load balancing strategy.
        
        Args:
            available_agents: List of available agent IDs
            task_requirements: Optional task requirements for capability-based routing
            
        Returns:
            Selected agent ID or None if no suitable agent found
        """
        if not available_agents:
            return None

        # Filter to agents with known load information
        agents_with_load = [
            agent_id for agent_id in available_agents
            if agent_id in self.agent_loads
        ]

        if not agents_with_load:
            # Fall back to first available agent
            return available_agents[0]

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(agents_with_load)
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded_select(agents_with_load)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            return self._weighted_select(agents_with_load)
        elif self.strategy == LoadBalancingStrategy.CAPABILITY_BASED:
            return self._capability_based_select(agents_with_load, task_requirements)
        else:
            return agents_with_load[0]

    def _round_robin_select(self, agents: List[str]) -> str:
        """Round-robin selection"""
        agent = agents[self._round_robin_index % len(agents)]
        self._round_robin_index += 1
        return agent

    def _least_loaded_select(self, agents: List[str]) -> str:
        """Select agent with least load"""
        def get_load_score(agent_id: str) -> float:
            load = self.agent_loads[agent_id]
            if load.total_capacity == 0:
                return 1.0
            return load.active_tasks / load.total_capacity

        return min(agents, key=get_load_score)

    def _weighted_select(self, agents: List[str]) -> str:
        """Select agent based on weighted scoring"""
        def get_score(agent_id: str) -> float:
            load = self.agent_loads[agent_id]
            
            # Calculate utilization (lower is better)
            utilization = load.active_tasks / load.total_capacity if load.total_capacity > 0 else 1.0
            
            # Calculate resource usage (lower is better)
            resource_usage = (load.cpu_usage + load.memory_usage) / 2.0
            
            # Calculate performance (higher is better)
            performance = load.success_rate
            
            # Weighted score (lower is better)
            score = (utilization * 0.4) + (resource_usage * 0.3) - (performance * 0.3)
            return score

        return min(agents, key=get_score)

    def _capability_based_select(
        self,
        agents: List[str],
        task_requirements: Optional[Dict[str, Any]],
    ) -> str:
        """Select agent based on capabilities and load"""
        # For now, fall back to least loaded
        # In a real implementation, this would match task requirements to agent capabilities
        return self._least_loaded_select(agents)

    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent cluster"""
        if not self.agent_loads:
            return {
                "total_agents": 0,
                "total_capacity": 0,
                "total_active_tasks": 0,
                "avg_utilization": 0.0,
                "avg_cpu_usage": 0.0,
                "avg_memory_usage": 0.0,
            }

        total_capacity = sum(load.total_capacity for load in self.agent_loads.values())
        total_active = sum(load.active_tasks for load in self.agent_loads.values())
        
        avg_utilization = (
            total_active / total_capacity if total_capacity > 0 else 0.0
        )
        avg_cpu = sum(load.cpu_usage for load in self.agent_loads.values()) / len(
            self.agent_loads
        )
        avg_memory = sum(load.memory_usage for load in self.agent_loads.values()) / len(
            self.agent_loads
        )

        return {
            "total_agents": len(self.agent_loads),
            "total_capacity": total_capacity,
            "total_active_tasks": total_active,
            "avg_utilization": avg_utilization,
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory,
        }
