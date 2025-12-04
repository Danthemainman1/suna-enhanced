"""
FastAPI router for multi-agent collaboration endpoints.

This module provides REST API endpoints for running different
collaboration modes (debate, ensemble, pipeline, swarm, critique).
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Any
from pydantic import BaseModel, Field

from .debate import DebateMode
from .ensemble import EnsembleMode
from .pipeline import PipelineMode
from .swarm import SwarmMode
from .critique import CritiqueMode
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


# Request Models
class CollaborationRequest(BaseModel):
    """Base request for collaboration."""
    task: CollaborationTask
    agents: list[CollaborationAgent]
    config: Optional[dict] = None


class DebateRequest(CollaborationRequest):
    """Request for debate mode."""
    config: Optional[dict] = Field(None, description="Debate configuration")


class EnsembleRequest(CollaborationRequest):
    """Request for ensemble mode."""
    config: Optional[dict] = Field(None, description="Ensemble configuration")


class PipelineRequest(CollaborationRequest):
    """Request for pipeline mode."""
    config: Optional[dict] = Field(None, description="Pipeline configuration")


class SwarmRequest(CollaborationRequest):
    """Request for swarm mode."""
    config: Optional[dict] = Field(None, description="Swarm configuration")


class CritiqueRequest(CollaborationRequest):
    """Request for critique mode."""
    config: Optional[dict] = Field(None, description="Critique configuration")


# Initialize components
router = APIRouter(prefix="/collaborate", tags=["collaboration"])
debate_mode = DebateMode()
ensemble_mode = EnsembleMode()
pipeline_mode = PipelineMode()
swarm_mode = SwarmMode()
critique_mode = CritiqueMode()


# Collaboration Endpoints
@router.post("/debate", response_model=CollaborationResult)
async def run_debate(request: DebateRequest):
    """
    Run debate collaboration mode.
    
    Agents argue different perspectives, and a judge decides the winner.
    
    Args:
        request: Debate request with task, agents, and config
        
    Returns:
        CollaborationResult: Debate results
    """
    try:
        result = await debate_mode.execute(
            request.task,
            request.agents,
            request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ensemble", response_model=CollaborationResult)
async def run_ensemble(request: EnsembleRequest):
    """
    Run ensemble collaboration mode.
    
    Multiple agents work in parallel, and results are merged.
    
    Args:
        request: Ensemble request with task, agents, and config
        
    Returns:
        CollaborationResult: Ensemble results
    """
    try:
        result = await ensemble_mode.execute(
            request.task,
            request.agents,
            request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline", response_model=CollaborationResult)
async def run_pipeline(request: PipelineRequest):
    """
    Run pipeline collaboration mode.
    
    Sequential handoff between specialist agents.
    
    Args:
        request: Pipeline request with task, agents, and config
        
    Returns:
        CollaborationResult: Pipeline results
    """
    try:
        result = await pipeline_mode.execute(
            request.task,
            request.agents,
            request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/swarm", response_model=CollaborationResult)
async def run_swarm(request: SwarmRequest):
    """
    Run swarm collaboration mode.
    
    Dynamic self-organizing agent teams.
    
    Args:
        request: Swarm request with task, agents, and config
        
    Returns:
        CollaborationResult: Swarm results
    """
    try:
        result = await swarm_mode.execute(
            request.task,
            request.agents,
            request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/critique", response_model=CollaborationResult)
async def run_critique(request: CritiqueRequest):
    """
    Run critique collaboration mode.
    
    One agent works while others review and improve.
    
    Args:
        request: Critique request with task, agents, and config
        
    Returns:
        CollaborationResult: Critique results
    """
    try:
        result = await critique_mode.execute(
            request.task,
            request.agents,
            request.config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Info Endpoints
@router.get("/modes")
async def list_collaboration_modes():
    """
    List all available collaboration modes.
    
    Returns:
        dict: Available collaboration modes and their descriptions
    """
    return {
        "modes": [
            {
                "name": debate_mode.name,
                "description": debate_mode.description
            },
            {
                "name": ensemble_mode.name,
                "description": ensemble_mode.description
            },
            {
                "name": pipeline_mode.name,
                "description": pipeline_mode.description
            },
            {
                "name": swarm_mode.name,
                "description": swarm_mode.description
            },
            {
                "name": critique_mode.name,
                "description": critique_mode.description
            }
        ]
    }


@router.get("/modes/{mode_name}")
async def get_mode_info(mode_name: str):
    """
    Get detailed information about a collaboration mode.
    
    Args:
        mode_name: Name of the collaboration mode
        
    Returns:
        dict: Mode information and configuration options
    """
    modes = {
        "debate": {
            "name": debate_mode.name,
            "description": debate_mode.description,
            "config_schema": DebateConfig.model_json_schema(),
            "min_agents": 2,
            "recommended_agents": "2-4"
        },
        "ensemble": {
            "name": ensemble_mode.name,
            "description": ensemble_mode.description,
            "config_schema": EnsembleConfig.model_json_schema(),
            "min_agents": 2,
            "recommended_agents": "3-5"
        },
        "pipeline": {
            "name": pipeline_mode.name,
            "description": pipeline_mode.description,
            "config_schema": PipelineConfig.model_json_schema(),
            "min_agents": 2,
            "recommended_agents": "2-5"
        },
        "swarm": {
            "name": swarm_mode.name,
            "description": swarm_mode.description,
            "config_schema": SwarmConfig.model_json_schema(),
            "min_agents": 1,
            "recommended_agents": "3-10"
        },
        "critique": {
            "name": critique_mode.name,
            "description": critique_mode.description,
            "config_schema": CritiqueConfig.model_json_schema(),
            "min_agents": 2,
            "recommended_agents": "2-4"
        }
    }
    
    if mode_name not in modes:
        raise HTTPException(
            status_code=404,
            detail=f"Collaboration mode '{mode_name}' not found"
        )
    
    return modes[mode_name]


# Initialize function for app startup
async def initialize():
    """Initialize the collaboration API components."""
    pass


# Cleanup function for app shutdown
async def cleanup():
    """Cleanup collaboration API components."""
    pass
