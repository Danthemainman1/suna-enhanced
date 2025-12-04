"""
Base class for multi-agent collaboration modes.

This module provides the abstract base class that all collaboration
modes must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime
from .models import CollaborationResult, CollaborationTask, CollaborationAgent


class CollaborationModeBase(ABC):
    """
    Abstract base class for multi-agent collaboration modes.
    
    All collaboration modes (debate, ensemble, pipeline, etc.) must
    inherit from this class and implement the execute method.
    """
    
    name: str = "base"
    description: str = "Base collaboration mode"
    
    def __init__(self):
        """Initialize the collaboration mode."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute the collaboration mode.
        
        Args:
            task: The task to be performed collaboratively
            agents: List of agents participating in collaboration
            config: Optional configuration for this mode
            
        Returns:
            CollaborationResult: The result of the collaboration
        """
        pass
    
    def _create_result(
        self,
        mode: str,
        agents: list[CollaborationAgent],
        final_output: Any,
        individual_outputs: list[dict],
        start_time: datetime,
        metadata: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Create a collaboration result.
        
        Args:
            mode: Collaboration mode name
            agents: Participating agents
            final_output: Final collaborative output
            individual_outputs: Individual agent outputs
            start_time: When collaboration started
            metadata: Additional metadata
            
        Returns:
            CollaborationResult: The created result
        """
        end_time = datetime.utcnow()
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return CollaborationResult(
            mode=mode,
            agents_used=[agent.id for agent in agents],
            final_output=final_output,
            individual_outputs=individual_outputs,
            metadata=metadata or {},
            execution_time_ms=execution_time_ms,
            started_at=start_time,
            completed_at=end_time
        )
    
    async def validate_agents(
        self,
        agents: list[CollaborationAgent],
        min_agents: int = 1,
        max_agents: Optional[int] = None
    ) -> bool:
        """
        Validate that the agent list meets requirements.
        
        Args:
            agents: List of agents to validate
            min_agents: Minimum number of agents required
            max_agents: Maximum number of agents allowed (None = no limit)
            
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if len(agents) < min_agents:
            raise ValueError(f"{self.name} requires at least {min_agents} agents")
        
        if max_agents and len(agents) > max_agents:
            raise ValueError(f"{self.name} allows at most {max_agents} agents")
        
        return True
    
    async def validate_config(self, config: Optional[dict]) -> bool:
        """
        Validate configuration for this mode.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if valid
        """
        # Base implementation does no validation
        return True
