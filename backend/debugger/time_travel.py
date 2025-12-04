"""
Time travel debugging for agent execution.

This module provides the ability to replay past executions, step backward
and forward through history, and re-run tasks from specific points.
"""

import uuid
from typing import Optional
from datetime import datetime
from .models import ExecutionSnapshot, ReplaySession


class TimeTravelDebugger:
    """
    Time travel debugger for agent execution.
    
    Allows replaying past executions, stepping through history, and
    re-running tasks from specific checkpoints.
    """
    
    def __init__(self):
        """Initialize the time travel debugger."""
        self._snapshots: dict[str, list[ExecutionSnapshot]] = {}
        self._replay_sessions: dict[str, ReplaySession] = {}
    
    async def get_execution_history(self, task_id: str) -> list[ExecutionSnapshot]:
        """
        Get all snapshots from a task execution.
        
        Args:
            task_id: ID of the task
            
        Returns:
            list[ExecutionSnapshot]: All execution snapshots
        """
        return self._snapshots.get(task_id, [])
    
    async def create_replay(self, task_id: str) -> ReplaySession:
        """
        Create a replay session for a completed task.
        
        Args:
            task_id: ID of the task to replay
            
        Returns:
            ReplaySession: The created replay session
        """
        snapshots = await self.get_execution_history(task_id)
        
        if not snapshots:
            raise ValueError(f"No execution history found for task {task_id}")
        
        session_id = str(uuid.uuid4())
        
        session = ReplaySession(
            id=session_id,
            task_id=task_id,
            current_snapshot_index=0,
            total_snapshots=len(snapshots),
            snapshots=snapshots
        )
        
        self._replay_sessions[session_id] = session
        
        return session
    
    async def step_forward(self, session_id: str) -> ExecutionSnapshot:
        """
        Move to next snapshot.
        
        Args:
            session_id: ID of the replay session
            
        Returns:
            ExecutionSnapshot: The next snapshot
        """
        if session_id not in self._replay_sessions:
            raise ValueError(f"Replay session {session_id} not found")
        
        session = self._replay_sessions[session_id]
        
        if session.current_snapshot_index >= session.total_snapshots - 1:
            raise ValueError("Already at the last snapshot")
        
        session.current_snapshot_index += 1
        
        return session.snapshots[session.current_snapshot_index]
    
    async def step_backward(self, session_id: str) -> ExecutionSnapshot:
        """
        Move to previous snapshot.
        
        Args:
            session_id: ID of the replay session
            
        Returns:
            ExecutionSnapshot: The previous snapshot
        """
        if session_id not in self._replay_sessions:
            raise ValueError(f"Replay session {session_id} not found")
        
        session = self._replay_sessions[session_id]
        
        if session.current_snapshot_index <= 0:
            raise ValueError("Already at the first snapshot")
        
        session.current_snapshot_index -= 1
        
        return session.snapshots[session.current_snapshot_index]
    
    async def jump_to(self, session_id: str, step_number: int) -> ExecutionSnapshot:
        """
        Jump to specific step.
        
        Args:
            session_id: ID of the replay session
            step_number: Step number to jump to
            
        Returns:
            ExecutionSnapshot: The snapshot at the specified step
        """
        if session_id not in self._replay_sessions:
            raise ValueError(f"Replay session {session_id} not found")
        
        session = self._replay_sessions[session_id]
        
        if step_number < 0 or step_number >= session.total_snapshots:
            raise ValueError(f"Invalid step number: {step_number}")
        
        session.current_snapshot_index = step_number
        
        return session.snapshots[session.current_snapshot_index]
    
    async def get_diff(self, snapshot_a_id: str, snapshot_b_id: str) -> dict:
        """
        Get diff between two snapshots.
        
        Args:
            snapshot_a_id: ID of first snapshot
            snapshot_b_id: ID of second snapshot
            
        Returns:
            dict: Differences between snapshots
        """
        # Find snapshots across all tasks
        snapshot_a = None
        snapshot_b = None
        
        for snapshots in self._snapshots.values():
            for snapshot in snapshots:
                if snapshot.id == snapshot_a_id:
                    snapshot_a = snapshot
                if snapshot.id == snapshot_b_id:
                    snapshot_b = snapshot
        
        if not snapshot_a or not snapshot_b:
            raise ValueError("One or both snapshots not found")
        
        # Compute differences
        diff = {
            "snapshot_a": {
                "id": snapshot_a.id,
                "step_number": snapshot_a.step_number,
                "action": snapshot_a.action,
                "timestamp": snapshot_a.timestamp.isoformat()
            },
            "snapshot_b": {
                "id": snapshot_b.id,
                "step_number": snapshot_b.step_number,
                "action": snapshot_b.action,
                "timestamp": snapshot_b.timestamp.isoformat()
            },
            "state_changes": self._compute_state_diff(
                snapshot_a.state,
                snapshot_b.state
            )
        }
        
        return diff
    
    def _compute_state_diff(self, state_a: dict, state_b: dict) -> dict:
        """
        Compute differences between two state dictionaries.
        
        Args:
            state_a: First state
            state_b: Second state
            
        Returns:
            dict: Differences
        """
        added = {}
        removed = {}
        changed = {}
        
        # Find added and changed keys
        for key in state_b:
            if key not in state_a:
                added[key] = state_b[key]
            elif state_a[key] != state_b[key]:
                changed[key] = {
                    "old": state_a[key],
                    "new": state_b[key]
                }
        
        # Find removed keys
        for key in state_a:
            if key not in state_b:
                removed[key] = state_a[key]
        
        return {
            "added": added,
            "removed": removed,
            "changed": changed
        }
    
    async def replay_from(self, task_id: str, snapshot_id: str) -> str:
        """
        Re-run task from a specific snapshot.
        
        Args:
            task_id: ID of the original task
            snapshot_id: ID of the snapshot to start from
            
        Returns:
            str: ID of the new task
        """
        # Find the snapshot
        snapshots = self._snapshots.get(task_id, [])
        snapshot = None
        
        for s in snapshots:
            if s.id == snapshot_id:
                snapshot = s
                break
        
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        # Generate new task ID
        new_task_id = str(uuid.uuid4())
        
        # In a real implementation, this would:
        # 1. Restore the state from the snapshot
        # 2. Create a new task with that state
        # 3. Execute the task from that point
        
        return new_task_id
    
    def record_snapshot(self, task_id: str, snapshot: ExecutionSnapshot) -> None:
        """
        Record a snapshot for a task.
        
        Args:
            task_id: ID of the task
            snapshot: Snapshot to record
        """
        if task_id not in self._snapshots:
            self._snapshots[task_id] = []
        
        self._snapshots[task_id].append(snapshot)
    
    async def get_current_snapshot(self, session_id: str) -> Optional[ExecutionSnapshot]:
        """
        Get the current snapshot in a replay session.
        
        Args:
            session_id: ID of the replay session
            
        Returns:
            ExecutionSnapshot or None: Current snapshot
        """
        if session_id not in self._replay_sessions:
            return None
        
        session = self._replay_sessions[session_id]
        
        if 0 <= session.current_snapshot_index < len(session.snapshots):
            return session.snapshots[session.current_snapshot_index]
        
        return None
