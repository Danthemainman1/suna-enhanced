"""
State inspector for detailed debugging analysis.

This module provides detailed inspection of agent execution state,
including variable inspection, memory analysis, and call stack traces.
"""

from typing import Any, Optional
from datetime import datetime


class StateInspector:
    """
    Provides detailed inspection of agent execution state.
    
    Allows examining variables, call stacks, memory usage, and other
    execution details for debugging purposes.
    """
    
    def __init__(self):
        """Initialize the state inspector."""
        self._state_cache: dict[str, dict] = {}
    
    async def inspect_variable(
        self,
        session_id: str,
        variable_name: str
    ) -> Optional[dict]:
        """
        Inspect a specific variable.
        
        Args:
            session_id: Debug session ID
            variable_name: Name of the variable to inspect
            
        Returns:
            dict or None: Variable details
        """
        state = self._state_cache.get(session_id, {})
        variables = state.get("variables", {})
        
        if variable_name not in variables:
            return None
        
        value = variables[variable_name]
        
        return {
            "name": variable_name,
            "value": value,
            "type": type(value).__name__,
            "size": len(str(value)),
            "is_mutable": self._is_mutable(value)
        }
    
    async def inspect_call_stack(self, session_id: str) -> list[dict]:
        """
        Inspect the call stack.
        
        Args:
            session_id: Debug session ID
            
        Returns:
            list[dict]: Call stack frames
        """
        state = self._state_cache.get(session_id, {})
        call_stack = state.get("call_stack", [])
        
        return [
            {
                "frame_id": i,
                "function": frame.get("function", "unknown"),
                "file": frame.get("file", "unknown"),
                "line": frame.get("line", 0),
                "locals": frame.get("locals", {})
            }
            for i, frame in enumerate(call_stack)
        ]
    
    async def inspect_memory(self, session_id: str) -> dict:
        """
        Inspect memory usage.
        
        Args:
            session_id: Debug session ID
            
        Returns:
            dict: Memory usage statistics
        """
        state = self._state_cache.get(session_id, {})
        
        # Calculate memory usage from cached state
        total_size = 0
        variable_sizes = {}
        
        variables = state.get("variables", {})
        for name, value in variables.items():
            size = len(str(value))
            variable_sizes[name] = size
            total_size += size
        
        return {
            "total_bytes": total_size,
            "variable_count": len(variables),
            "largest_variables": sorted(
                variable_sizes.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    async def inspect_performance(self, session_id: str) -> dict:
        """
        Inspect performance metrics.
        
        Args:
            session_id: Debug session ID
            
        Returns:
            dict: Performance metrics
        """
        state = self._state_cache.get(session_id, {})
        
        return {
            "execution_time_ms": state.get("execution_time_ms", 0),
            "step_count": state.get("step_count", 0),
            "tool_calls": state.get("tool_calls", 0),
            "average_step_time_ms": (
                state.get("execution_time_ms", 0) / max(state.get("step_count", 1), 1)
            )
        }
    
    async def get_object_details(
        self,
        session_id: str,
        object_path: str
    ) -> Optional[dict]:
        """
        Get detailed information about an object.
        
        Args:
            session_id: Debug session ID
            object_path: Path to object (e.g., "user.profile.name")
            
        Returns:
            dict or None: Object details
        """
        state = self._state_cache.get(session_id, {})
        variables = state.get("variables", {})
        
        # Navigate the object path
        obj = variables
        parts = object_path.split(".")
        
        try:
            for part in parts:
                if isinstance(obj, dict):
                    obj = obj[part]
                else:
                    obj = getattr(obj, part)
        except (KeyError, AttributeError):
            return None
        
        return {
            "path": object_path,
            "value": obj,
            "type": type(obj).__name__,
            "attributes": dir(obj) if hasattr(obj, "__dict__") else [],
            "is_callable": callable(obj),
            "doc": getattr(obj, "__doc__", None)
        }
    
    def cache_state(self, session_id: str, state: dict) -> None:
        """
        Cache state for inspection.
        
        Args:
            session_id: Debug session ID
            state: State to cache
        """
        self._state_cache[session_id] = state
    
    def clear_cache(self, session_id: str) -> None:
        """
        Clear cached state.
        
        Args:
            session_id: Debug session ID
        """
        self._state_cache.pop(session_id, None)
    
    def _is_mutable(self, value: Any) -> bool:
        """
        Check if a value is mutable.
        
        Args:
            value: Value to check
            
        Returns:
            bool: True if mutable
        """
        immutable_types = (str, int, float, bool, tuple, frozenset, bytes)
        return not isinstance(value, immutable_types)
