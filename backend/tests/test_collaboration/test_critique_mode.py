"""
Tests for critique collaboration mode.
"""

import pytest
from multi_agent.critique import CritiqueMode
from multi_agent.models import CollaborationTask, CollaborationAgent


@pytest.mark.asyncio
async def test_critique_mode_basic():
    """Test basic critique mode execution."""
    mode = CritiqueMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Write a technical document",
        requirements=["Clarity", "Accuracy"],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Writer", capabilities=["writing"]),
        CollaborationAgent(id="agent-2", name="Critic 1", capabilities=["review"]),
        CollaborationAgent(id="agent-3", name="Critic 2", capabilities=["review"])
    ]
    
    result = await mode.execute(task, agents)
    
    assert result.mode == "critique"
    assert len(result.agents_used) == 3
    assert "output" in result.final_output
    assert "iterations" in result.final_output


@pytest.mark.asyncio
async def test_critique_mode_iterations():
    """Test critique mode with multiple iterations."""
    mode = CritiqueMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Primary", capabilities=[]),
        CollaborationAgent(id="agent-2", name="Critic", capabilities=[])
    ]
    
    config = {
        "max_iterations": 3,
        "approval_threshold": 0.9
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "critique"
    assert result.final_output["iterations"] <= 3


@pytest.mark.asyncio
async def test_critique_mode_approval():
    """Test critique mode with low approval threshold."""
    mode = CritiqueMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Primary", capabilities=[]),
        CollaborationAgent(id="agent-2", name="Critic", capabilities=[])
    ]
    
    config = {
        "max_iterations": 5,
        "approval_threshold": 0.6  # Lower threshold for easier approval
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "critique"
    # With lower threshold, should be approved
    assert result.final_output.get("approved") is not None
