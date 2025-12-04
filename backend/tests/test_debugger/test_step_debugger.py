"""
Tests for step debugger.
"""

import pytest
from debugger.step_debugger import AgentDebugger
from debugger.models import DebugStatus, StepType


@pytest.mark.asyncio
async def test_attach_debugger():
    """Test attaching debugger to a task."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    
    assert session.agent_id == "agent-1"
    assert session.task_id == "task-1"
    assert session.status == DebugStatus.PAUSED
    assert session.current_step == 0
    assert session.total_steps == 0


@pytest.mark.asyncio
async def test_detach_debugger():
    """Test detaching debugger from a task."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    success = await debugger.detach(session.id)
    
    assert success is True


@pytest.mark.asyncio
async def test_pause_debugger():
    """Test pausing debugger."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    state = await debugger.pause(session.id)
    
    assert state.step_number == 0
    assert session.status == DebugStatus.PAUSED


@pytest.mark.asyncio
async def test_step_debugger():
    """Test stepping through execution."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    state = await debugger.step(session.id)
    
    assert state is not None
    assert session.current_step == 1


@pytest.mark.asyncio
async def test_continue_debugger():
    """Test continuing execution."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    await debugger.continue_run(session.id)
    
    assert session.status == DebugStatus.RUNNING


@pytest.mark.asyncio
async def test_get_variables():
    """Test getting variables in current scope."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    variables = await debugger.get_variables(session.id)
    
    assert isinstance(variables, dict)


@pytest.mark.asyncio
async def test_evaluate_expression():
    """Test evaluating an expression."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    
    # Should handle invalid expressions gracefully
    with pytest.raises(ValueError):
        await debugger.evaluate(session.id, "undefined_variable")


@pytest.mark.asyncio
async def test_get_state():
    """Test getting current state."""
    debugger = AgentDebugger()
    
    session = await debugger.attach("agent-1", "task-1")
    state = await debugger.get_state(session.id)
    
    assert state.step_number == 0
    assert state.step_type == StepType.THINKING
