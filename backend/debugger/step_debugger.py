"""
Step-through debugger for agent execution.

This module provides real-time debugging capabilities for running agents,
allowing pause, step, inspect state at each step.
"""

import asyncio
import uuid
from typing import Any, Optional
from datetime import datetime
from .models import DebugSession, DebugState, DebugStatus, StepType


class AgentDebugger:
    """
    Step-through debugger for agent execution.
    
    Provides real-time debugging capabilities including pause, step,
    continue, and state inspection for running agent tasks.
    """
    
    def __init__(self):
        """Initialize the agent debugger."""
        self._sessions: dict[str, DebugSession] = {}
        self._states: dict[str, list[DebugState]] = {}
        self._execution_locks: dict[str, asyncio.Event] = {}
        self._step_events: dict[str, asyncio.Event] = {}
    
    async def attach(self, agent_id: str, task_id: str) -> DebugSession:
        """
        Attach debugger to a running task.
        
        Args:
            agent_id: ID of the agent to debug
            task_id: ID of the task to debug
            
        Returns:
            DebugSession: The created debug session
        """
        session_id = str(uuid.uuid4())
        
        session = DebugSession(
            id=session_id,
            agent_id=agent_id,
            task_id=task_id,
            status=DebugStatus.PAUSED,
            current_step=0,
            total_steps=0,
            created_at=datetime.utcnow()
        )
        
        self._sessions[session_id] = session
        self._states[session_id] = []
        self._execution_locks[session_id] = asyncio.Event()
        self._step_events[session_id] = asyncio.Event()
        
        # Pause execution immediately
        self._execution_locks[session_id].clear()
        
        return session
    
    async def detach(self, session_id: str) -> bool:
        """
        Detach debugger and let task run freely.
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            bool: True if successfully detached
        """
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        session.status = DebugStatus.DETACHED
        
        # Release any locks to allow execution to continue
        if session_id in self._execution_locks:
            self._execution_locks[session_id].set()
        
        # Cleanup
        self._sessions.pop(session_id, None)
        self._states.pop(session_id, None)
        self._execution_locks.pop(session_id, None)
        self._step_events.pop(session_id, None)
        
        return True
    
    async def pause(self, session_id: str) -> DebugState:
        """
        Pause execution at current step.
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            DebugState: Current execution state
        """
        if session_id not in self._sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self._sessions[session_id]
        session.status = DebugStatus.PAUSED
        
        # Clear the execution lock to pause
        self._execution_locks[session_id].clear()
        
        return await self.get_state(session_id)
    
    async def step(self, session_id: str) -> DebugState:
        """
        Execute one step and pause.
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            DebugState: State after executing the step
        """
        if session_id not in self._sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self._sessions[session_id]
        session.status = DebugStatus.RUNNING
        
        # Allow one step to execute
        self._step_events[session_id].set()
        
        # Wait a moment for step to execute
        await asyncio.sleep(0.1)
        
        # Pause again
        session.status = DebugStatus.PAUSED
        self._step_events[session_id].clear()
        
        session.current_step += 1
        
        return await self.get_state(session_id)
    
    async def step_over(self, session_id: str) -> DebugState:
        """
        Step over tool calls (don't step into).
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            DebugState: State after stepping over
        """
        # For now, step_over behaves like regular step
        # In a full implementation, this would skip nested tool execution
        return await self.step(session_id)
    
    async def continue_run(self, session_id: str) -> None:
        """
        Continue execution until next breakpoint or end.
        
        Args:
            session_id: ID of the debug session
        """
        if session_id not in self._sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self._sessions[session_id]
        session.status = DebugStatus.RUNNING
        
        # Release the execution lock
        self._execution_locks[session_id].set()
    
    async def get_state(self, session_id: str) -> DebugState:
        """
        Get current execution state.
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            DebugState: Current state
        """
        if session_id not in self._sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self._sessions[session_id]
        states = self._states.get(session_id, [])
        
        if states and session.current_step < len(states):
            return states[session.current_step]
        
        # Return a placeholder state if no recorded states
        return DebugState(
            step_number=session.current_step,
            step_type=StepType.THINKING,
            description="Current execution state",
            input_data={},
            output_data=None,
            variables={},
            timestamp=datetime.utcnow()
        )
    
    async def get_variables(self, session_id: str) -> dict:
        """
        Get all variables in current scope.
        
        Args:
            session_id: ID of the debug session
            
        Returns:
            dict: Variables in current scope
        """
        state = await self.get_state(session_id)
        return state.variables
    
    async def evaluate(self, session_id: str, expression: str) -> Any:
        """
        Evaluate expression in current context.
        
        Args:
            session_id: ID of the debug session
            expression: Expression to evaluate
            
        Returns:
            Any: Result of evaluation
        """
        variables = await self.get_variables(session_id)
        
        try:
            # Safe evaluation with limited scope
            # In production, use a safer evaluation method
            result = eval(expression, {"__builtins__": {}}, variables)
            return result
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression: {str(e)}")
    
    def record_state(self, session_id: str, state: DebugState) -> None:
        """
        Record a state for a debug session.
        
        Args:
            session_id: ID of the debug session
            state: State to record
        """
        if session_id in self._states:
            self._states[session_id].append(state)
            
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.total_steps = len(self._states[session_id])
    
    async def wait_for_step(self, session_id: str) -> None:
        """
        Wait for step event when in step mode.
        
        Args:
            session_id: ID of the debug session
        """
        if session_id in self._step_events:
            await self._step_events[session_id].wait()
    
    async def wait_for_continue(self, session_id: str) -> None:
        """
        Wait for continue event when paused.
        
        Args:
            session_id: ID of the debug session
        """
        if session_id in self._execution_locks:
            await self._execution_locks[session_id].wait()
