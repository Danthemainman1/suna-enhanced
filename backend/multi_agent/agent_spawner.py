"""
Agent Spawner - Dynamically spawn specialized agents

Creates and manages agent instances on-demand based on workload and requirements.
"""

import logging
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentSpawner:
    """
    Dynamically spawn and manage agent instances.
    
    Features:
    - On-demand agent creation
    - Agent pool management
    - Resource allocation
    - Automatic scaling
    """

    def __init__(self, max_agents: int = 10):
        self.max_agents = max_agents
        self.active_agents: Dict[str, Any] = {}
        self.agent_count = 0

    async def spawn_agent(
        self,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Spawn a new agent instance.
        
        Args:
            agent_type: Type of agent to spawn
            config: Configuration for the agent
            
        Returns:
            Agent ID of the spawned agent
        """
        if len(self.active_agents) >= self.max_agents:
            raise RuntimeError(f"Maximum number of agents ({self.max_agents}) reached")

        agent_id = f"{agent_type}_{self.agent_count}_{int(datetime.utcnow().timestamp())}"
        self.agent_count += 1

        logger.info(f"Spawning agent: {agent_id} (type: {agent_type})")

        # Simulate agent creation
        agent_data = {
            "id": agent_id,
            "type": agent_type,
            "config": config or {},
            "created_at": datetime.utcnow(),
            "status": "active",
        }

        self.active_agents[agent_id] = agent_data
        return agent_id

    async def terminate_agent(self, agent_id: str):
        """Terminate an agent instance"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")

        logger.info(f"Terminating agent: {agent_id}")
        del self.active_agents[agent_id]

    async def get_agent_pool_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent pool"""
        return {
            "active_agents": len(self.active_agents),
            "max_agents": self.max_agents,
            "utilization": len(self.active_agents) / self.max_agents,
        }
