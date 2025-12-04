"""
Tests for time travel debugger.
"""

import pytest
from debugger.time_travel import TimeTravelDebugger
from debugger.models import ExecutionSnapshot
from datetime import datetime


@pytest.mark.asyncio
async def test_get_execution_history():
    """Test getting execution history."""
    debugger = TimeTravelDebugger()
    
    # Add some snapshots
    snapshot = ExecutionSnapshot(
        id="snap-1",
        task_id="task-1",
        step_number=1,
        timestamp=datetime.utcnow(),
        state={"key": "value"},
        action="test_action",
        result={"output": "test"}
    )
    debugger.record_snapshot("task-1", snapshot)
    
    history = await debugger.get_execution_history("task-1")
    
    assert len(history) == 1
    assert history[0].id == "snap-1"


@pytest.mark.asyncio
async def test_create_replay():
    """Test creating a replay session."""
    debugger = TimeTravelDebugger()
    
    # Add snapshots
    for i in range(3):
        snapshot = ExecutionSnapshot(
            id=f"snap-{i}",
            task_id="task-1",
            step_number=i,
            timestamp=datetime.utcnow(),
            state={"step": i},
            action=f"action-{i}",
            result=None
        )
        debugger.record_snapshot("task-1", snapshot)
    
    session = await debugger.create_replay("task-1")
    
    assert session.task_id == "task-1"
    assert session.total_snapshots == 3
    assert session.current_snapshot_index == 0


@pytest.mark.asyncio
async def test_step_forward():
    """Test stepping forward in replay."""
    debugger = TimeTravelDebugger()
    
    # Add snapshots
    for i in range(3):
        snapshot = ExecutionSnapshot(
            id=f"snap-{i}",
            task_id="task-1",
            step_number=i,
            timestamp=datetime.utcnow(),
            state={"step": i},
            action=f"action-{i}",
            result=None
        )
        debugger.record_snapshot("task-1", snapshot)
    
    session = await debugger.create_replay("task-1")
    snapshot = await debugger.step_forward(session.id)
    
    assert snapshot.step_number == 1
    assert session.current_snapshot_index == 1


@pytest.mark.asyncio
async def test_step_backward():
    """Test stepping backward in replay."""
    debugger = TimeTravelDebugger()
    
    # Add snapshots
    for i in range(3):
        snapshot = ExecutionSnapshot(
            id=f"snap-{i}",
            task_id="task-1",
            step_number=i,
            timestamp=datetime.utcnow(),
            state={"step": i},
            action=f"action-{i}",
            result=None
        )
        debugger.record_snapshot("task-1", snapshot)
    
    session = await debugger.create_replay("task-1")
    
    # Move forward first
    await debugger.step_forward(session.id)
    await debugger.step_forward(session.id)
    
    # Then backward
    snapshot = await debugger.step_backward(session.id)
    
    assert snapshot.step_number == 1
    assert session.current_snapshot_index == 1


@pytest.mark.asyncio
async def test_jump_to():
    """Test jumping to a specific step."""
    debugger = TimeTravelDebugger()
    
    # Add snapshots
    for i in range(5):
        snapshot = ExecutionSnapshot(
            id=f"snap-{i}",
            task_id="task-1",
            step_number=i,
            timestamp=datetime.utcnow(),
            state={"step": i},
            action=f"action-{i}",
            result=None
        )
        debugger.record_snapshot("task-1", snapshot)
    
    session = await debugger.create_replay("task-1")
    snapshot = await debugger.jump_to(session.id, 3)
    
    assert snapshot.step_number == 3
    assert session.current_snapshot_index == 3


@pytest.mark.asyncio
async def test_get_diff():
    """Test getting diff between snapshots."""
    debugger = TimeTravelDebugger()
    
    # Add snapshots
    snapshot1 = ExecutionSnapshot(
        id="snap-1",
        task_id="task-1",
        step_number=1,
        timestamp=datetime.utcnow(),
        state={"key1": "value1", "key2": "value2"},
        action="action-1",
        result=None
    )
    snapshot2 = ExecutionSnapshot(
        id="snap-2",
        task_id="task-1",
        step_number=2,
        timestamp=datetime.utcnow(),
        state={"key1": "value1_changed", "key3": "value3"},
        action="action-2",
        result=None
    )
    
    debugger.record_snapshot("task-1", snapshot1)
    debugger.record_snapshot("task-1", snapshot2)
    
    diff = await debugger.get_diff("snap-1", "snap-2")
    
    assert "state_changes" in diff
    assert "changed" in diff["state_changes"]
    assert "added" in diff["state_changes"]
