"""
Tests for debate collaboration mode.
"""

import pytest
from multi_agent.debate import DebateMode
from multi_agent.models import CollaborationTask, CollaborationAgent


@pytest.mark.asyncio
async def test_debate_mode_basic():
    """Test basic debate mode execution."""
    mode = DebateMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Should we use TypeScript or JavaScript?",
        requirements=["Consider maintainability", "Consider performance"],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(
            id="agent-1",
            name="Agent Pro",
            capabilities=["debate"]
        ),
        CollaborationAgent(
            id="agent-2",
            name="Agent Con",
            capabilities=["debate"]
        )
    ]
    
    result = await mode.execute(task, agents, {"rounds": 2})
    
    assert result.mode == "debate"
    assert len(result.agents_used) == 2
    assert "winner" in result.final_output
    assert len(result.individual_outputs) == 2


@pytest.mark.asyncio
async def test_debate_mode_with_judge():
    """Test debate mode with specified judge."""
    mode = DebateMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test debate task",
        requirements=[],
        constraints={},
        context={}
    )
    
    agents = [
        CollaborationAgent(id="agent-1", name="Agent 1", capabilities=[]),
        CollaborationAgent(id="agent-2", name="Agent 2", capabilities=[])
    ]
    
    config = {
        "rounds": 1,
        "judge_agent_id": "judge-1"
    }
    
    result = await mode.execute(task, agents, config)
    
    assert result.mode == "debate"
    assert result.metadata["rounds"] == 1


@pytest.mark.asyncio
async def test_debate_mode_validation():
    """Test debate mode agent validation."""
    mode = DebateMode()
    
    task = CollaborationTask(
        id="task-1",
        description="Test task",
        requirements=[],
        constraints={},
        context={}
    )
    
    # Only one agent - should fail
    agents = [
        CollaborationAgent(id="agent-1", name="Agent 1", capabilities=[])
    ]
    
    with pytest.raises(ValueError):
        await mode.execute(task, agents)
