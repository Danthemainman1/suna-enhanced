"""
Tests for pipeline collaboration mode.
"""

import pytest
from multi_agent.pipeline import PipelineMode
from multi_agent.models import CollaborationTask, CollaborationAgent


@pytest.mark.asyncio
async def test_pipeline_mode_basic():
    """Test basic pipeline mode execution."""
    mode = PipelineMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Multi-stage processing task",
        requirements=["Stage 1", "Stage 2", "Stage 3"],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Stage 1 Agent", capabilities=["stage1"]),
        CollaborationAgent(id="agent-2", name="Stage 2 Agent", capabilities=["stage2"]),
        CollaborationAgent(id="agent-3", name="Stage 3 Agent", capabilities=["stage3"])
    ]
    
    result = await mode.execute(task, agents)
    
    assert result.mode == "pipeline"
    assert len(result.agents_used) == 3
    assert len(result.individual_outputs) == 3


@pytest.mark.asyncio
async def test_pipeline_structured_handoff():
    """Test pipeline with structured handoff format."""
    mode = PipelineMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Agent 1", capabilities=[]),
        CollaborationAgent(id="agent-2", name="Agent 2", capabilities=[])
    ]
    
    config = {
        "handoff_format": "structured"
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "pipeline"
    assert result.metadata["handoff_format"] == "structured"


@pytest.mark.asyncio
async def test_pipeline_natural_handoff():
    """Test pipeline with natural language handoff."""
    mode = PipelineMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Agent 1", capabilities=[]),
        CollaborationAgent(id="agent-2", name="Agent 2", capabilities=[])
    ]
    
    config = {
        "handoff_format": "natural"
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "pipeline"
    assert result.metadata["handoff_format"] == "natural"
