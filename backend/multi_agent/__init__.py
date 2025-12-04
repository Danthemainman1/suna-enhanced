"""
Suna Ultra Multi-Agent Orchestration System

This module provides advanced multi-agent coordination capabilities that surpass
traditional single-agent systems. It enables multiple specialized agents to work
together, communicate, and coordinate on complex tasks.
"""

from .orchestrator import AgentOrchestrator
from .agent_registry import AgentRegistry
from .task_decomposer import TaskDecomposer
from .agent_spawner import AgentSpawner
from .communication_bus import CommunicationBus
from .consensus_engine import ConsensusEngine
from .load_balancer import LoadBalancer

# Collaboration modes
from .collaboration_modes import CollaborationModeBase
from .debate import DebateMode
from .ensemble import EnsembleMode
from .pipeline import PipelineMode
from .swarm import SwarmMode
from .critique import CritiqueMode

# Models
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    DebateConfig,
    EnsembleConfig,
    PipelineConfig,
    SwarmConfig,
    CritiqueConfig,
)

__all__ = [
    'AgentOrchestrator',
    'AgentRegistry',
    'TaskDecomposer',
    'AgentSpawner',
    'CommunicationBus',
    'ConsensusEngine',
    'LoadBalancer',
    'CollaborationModeBase',
    'DebateMode',
    'EnsembleMode',
    'PipelineMode',
    'SwarmMode',
    'CritiqueMode',
    'CollaborationResult',
    'CollaborationTask',
    'CollaborationAgent',
    'DebateConfig',
    'EnsembleConfig',
    'PipelineConfig',
    'SwarmConfig',
    'CritiqueConfig',
]
