"""
Swarm collaboration mode.

Dynamic self-organizing agent teams that decompose and tackle subtasks.
"""

import uuid
import asyncio
from typing import Optional, Any
from datetime import datetime
from .collaboration_modes import CollaborationModeBase
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    SwarmConfig,
    SubTask,
    BlackboardMessage,
    CoordinationStrategy
)


class SwarmMode(CollaborationModeBase):
    """
    Swarm collaboration mode.
    
    Agents self-organize to tackle a complex task. The task is decomposed
    into subtasks, agents claim subtasks based on capabilities, and they
    coordinate via a shared blackboard or message passing.
    """
    
    name = "swarm"
    description = "Dynamic self-organizing agent teams"
    
    def __init__(self):
        """Initialize swarm mode."""
        super().__init__()
        self._blackboard: list[BlackboardMessage] = []
    
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute swarm mode.
        
        Args:
            task: The task to decompose and solve
            agents: Initial agent swarm
            config: Swarm configuration
            
        Returns:
            CollaborationResult: Swarm results
        """
        start_time = datetime.utcnow()
        
        # Validate agents
        await self.validate_agents(agents, min_agents=1)
        
        # Parse config
        swarm_config = SwarmConfig(**(config or {}))
        
        # Decompose task into subtasks
        subtasks = await self._decompose_task(task, swarm_config)
        
        # Agents claim subtasks
        assignments = await self._assign_subtasks(
            subtasks,
            agents,
            swarm_config
        )
        
        # Execute subtasks with coordination
        if swarm_config.coordination == CoordinationStrategy.BLACKBOARD:
            results = await self._execute_with_blackboard(
                assignments,
                agents,
                swarm_config
            )
        else:
            results = await self._execute_with_messages(
                assignments,
                agents,
                swarm_config
            )
        
        # Aggregate results
        final_output = await self._aggregate_results(
            subtasks,
            results,
            swarm_config
        )
        
        # Collect individual outputs
        individual_outputs = [
            {
                "agent_id": agent.id,
                "subtasks_completed": [
                    st.id for st in subtasks if st.claimed_by == agent.id
                ],
                "results": [
                    {"subtask_id": st.id, "result": st.result}
                    for st in subtasks if st.claimed_by == agent.id
                ]
            }
            for agent in agents
        ]
        
        # Create result
        return self._create_result(
            mode=self.name,
            agents=agents,
            final_output=final_output,
            individual_outputs=individual_outputs,
            start_time=start_time,
            metadata={
                "total_subtasks": len(subtasks),
                "completed_subtasks": sum(1 for st in subtasks if st.status == "completed"),
                "coordination": swarm_config.coordination.value,
                "blackboard_messages": len(self._blackboard)
            }
        )
    
    async def _decompose_task(
        self,
        task: CollaborationTask,
        config: SwarmConfig
    ) -> list[SubTask]:
        """
        Decompose task into subtasks.
        
        Args:
            task: Task to decompose
            config: Swarm configuration
            
        Returns:
            list[SubTask]: Decomposed subtasks
        """
        # In a real implementation, this would use an LLM to intelligently
        # decompose the task based on complexity and agent capabilities
        
        # For now, create simple placeholder subtasks
        subtasks = []
        
        # Create 3-5 subtasks based on task description
        num_subtasks = min(len(task.requirements) + 2, 5)
        
        for i in range(num_subtasks):
            subtask = SubTask(
                id=str(uuid.uuid4()),
                description=f"Subtask {i + 1}: Part of {task.description}",
                status="pending",
                dependencies=[]
            )
            subtasks.append(subtask)
        
        return subtasks
    
    async def _assign_subtasks(
        self,
        subtasks: list[SubTask],
        agents: list[CollaborationAgent],
        config: SwarmConfig
    ) -> dict[str, list[SubTask]]:
        """
        Assign subtasks to agents based on capabilities.
        
        Args:
            subtasks: Subtasks to assign
            agents: Available agents
            config: Swarm configuration
            
        Returns:
            dict: Mapping of agent_id to assigned subtasks
        """
        assignments: dict[str, list[SubTask]] = {
            agent.id: [] for agent in agents
        }
        
        # Simple round-robin assignment
        # In a real implementation, this would consider agent capabilities
        for i, subtask in enumerate(subtasks):
            agent = agents[i % len(agents)]
            subtask.claimed_by = agent.id
            assignments[agent.id].append(subtask)
        
        return assignments
    
    async def _execute_with_blackboard(
        self,
        assignments: dict[str, list[SubTask]],
        agents: list[CollaborationAgent],
        config: SwarmConfig
    ) -> dict[str, Any]:
        """
        Execute with blackboard coordination.
        
        Args:
            assignments: Subtask assignments
            agents: Agent swarm
            config: Swarm configuration
            
        Returns:
            dict: Execution results
        """
        # Clear blackboard
        self._blackboard = []
        
        # Execute all agents in parallel
        tasks = []
        for agent in agents:
            agent_subtasks = assignments.get(agent.id, [])
            if agent_subtasks:
                tasks.append(
                    self._execute_agent_subtasks(
                        agent,
                        agent_subtasks,
                        config
                    )
                )
        
        await asyncio.gather(*tasks)
        
        return {"blackboard_messages": len(self._blackboard)}
    
    async def _execute_with_messages(
        self,
        assignments: dict[str, list[SubTask]],
        agents: list[CollaborationAgent],
        config: SwarmConfig
    ) -> dict[str, Any]:
        """
        Execute with message passing coordination.
        
        Args:
            assignments: Subtask assignments
            agents: Agent swarm
            config: Swarm configuration
            
        Returns:
            dict: Execution results
        """
        # Similar to blackboard but with direct messages
        # For now, use same implementation
        return await self._execute_with_blackboard(
            assignments,
            agents,
            config
        )
    
    async def _execute_agent_subtasks(
        self,
        agent: CollaborationAgent,
        subtasks: list[SubTask],
        config: SwarmConfig
    ) -> None:
        """
        Execute subtasks for one agent.
        
        Args:
            agent: Agent executing subtasks
            subtasks: Subtasks to execute
            config: Swarm configuration
        """
        for subtask in subtasks:
            # In a real implementation, invoke the actual agent
            # For now, simulate completion
            
            subtask.status = "in_progress"
            
            # Post to blackboard
            message = BlackboardMessage(
                id=str(uuid.uuid4()),
                from_agent=agent.id,
                message_type="status_update",
                content={
                    "subtask_id": subtask.id,
                    "status": "started"
                },
                timestamp=datetime.utcnow()
            )
            self._blackboard.append(message)
            
            # Simulate work
            await asyncio.sleep(0.1)
            
            # Complete subtask
            subtask.status = "completed"
            subtask.result = f"Result from {agent.name} for {subtask.description}"
            
            # Post completion to blackboard
            completion_message = BlackboardMessage(
                id=str(uuid.uuid4()),
                from_agent=agent.id,
                message_type="completion",
                content={
                    "subtask_id": subtask.id,
                    "result": subtask.result
                },
                timestamp=datetime.utcnow()
            )
            self._blackboard.append(completion_message)
    
    async def _aggregate_results(
        self,
        subtasks: list[SubTask],
        results: dict[str, Any],
        config: SwarmConfig
    ) -> Any:
        """
        Aggregate results from all subtasks.
        
        Args:
            subtasks: All subtasks
            results: Execution results
            config: Swarm configuration
            
        Returns:
            Any: Aggregated final result
        """
        # Collect all completed subtask results
        completed_results = [
            st.result for st in subtasks
            if st.status == "completed" and st.result
        ]
        
        # Check convergence
        completion_rate = len(completed_results) / len(subtasks) if subtasks else 0
        
        return {
            "completed_subtasks": len(completed_results),
            "total_subtasks": len(subtasks),
            "completion_rate": completion_rate,
            "converged": completion_rate >= config.convergence_threshold,
            "results": completed_results
        }
