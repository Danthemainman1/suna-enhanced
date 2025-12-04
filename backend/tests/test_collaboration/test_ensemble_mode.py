"""
Tests for ensemble collaboration mode.
"""

import pytest
from multi_agent.ensemble import EnsembleMode
from multi_agent.models import CollaborationTask, CollaborationAgent


@pytest.mark.asyncio
async def test_ensemble_mode_basic():
    """Test basic ensemble mode execution."""
    mode = EnsembleMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Analyze this data",
        requirements=["Accuracy", "Speed"],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Agent 1", capabilities=["analysis"]),
        CollaborationAgent(id="agent-2", name="Agent 2", capabilities=["analysis"]),
        CollaborationAgent(id="agent-3", name="Agent 3", capabilities=["analysis"])
    ]
    
    result = await mode.execute(task, agents)
    
    assert result.mode == "ensemble"
    assert len(result.agents_used) == 3
    assert len(result.individual_outputs) == 3


@pytest.mark.asyncio
async def test_ensemble_vote_strategy():
    """Test ensemble with vote merge strategy."""
    mode = EnsembleMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id=f"agent-{i}", name=f"Agent {i}", capabilities=[])
        for i in range(3)
    ]
    
    config = {
        "merge_strategy": "vote",
        "parallel_execution": True
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "ensemble"
    assert result.metadata["merge_strategy"] == "vote"


@pytest.mark.asyncio
async def test_ensemble_sequential():
    """Test ensemble with sequential execution."""
    mode = EnsembleMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id=f"agent-{i}", name=f"Agent {i}", capabilities=[])
        for i in range(2)
    ]
    
    config = {
        "parallel_execution": False
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "ensemble"
    assert len(result.individual_outputs) == 2
