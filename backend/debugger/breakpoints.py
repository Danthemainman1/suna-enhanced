"""
Breakpoint management for agent debugging.

This module provides breakpoint functionality for debugging,
including conditional breakpoints, step breakpoints, and tool breakpoints.
"""

import uuid
from typing import Optional
from datetime import datetime
from .models import Breakpoint, BreakpointType


class BreakpointManager:
    """
    Manages debugging breakpoints.
    
    Provides functionality to set, remove, enable/disable, and check
    breakpoints during agent execution.
    """
    
    def __init__(self):
        """Initialize the breakpoint manager."""
        self._breakpoints: dict[str, Breakpoint] = {}
        self._session_breakpoints: dict[str, list[str]] = {}
    
    async def add_breakpoint(
        self,
        session_id: str,
        breakpoint_type: BreakpointType,
        condition: Optional[str] = None,
        step_number: Optional[int] = None,
        tool_name: Optional[str] = None
    ) -> Breakpoint:
        """
        Add a new breakpoint.
        
        Args:
            session_id: Debug session ID
            breakpoint_type: Type of breakpoint
            condition: Condition expression (for conditional breakpoints)
            step_number: Step number (for step breakpoints)
            tool_name: Tool name (for tool breakpoints)
            
        Returns:
            Breakpoint: The created breakpoint
        """
        breakpoint_id = str(uuid.uuid4())
        
        breakpoint = Breakpoint(
            id=breakpoint_id,
            session_id=session_id,
            type=breakpoint_type,
            condition=condition,
            step_number=step_number,
            tool_name=tool_name,
            enabled=True,
            hit_count=0,
            created_at=datetime.utcnow()
        )
        
        self._breakpoints[breakpoint_id] = breakpoint
        
        if session_id not in self._session_breakpoints:
            self._session_breakpoints[session_id] = []
        
        self._session_breakpoints[session_id].append(breakpoint_id)
        
        return breakpoint
    
    async def remove_breakpoint(self, breakpoint_id: str) -> bool:
        """
        Remove a breakpoint.
        
        Args:
            breakpoint_id: ID of the breakpoint to remove
            
        Returns:
            bool: True if removed successfully
        """
        if breakpoint_id not in self._breakpoints:
            return False
        
        breakpoint = self._breakpoints[breakpoint_id]
        session_id = breakpoint.session_id
        
        # Remove from session list
        if session_id in self._session_breakpoints:
            if breakpoint_id in self._session_breakpoints[session_id]:
                self._session_breakpoints[session_id].remove(breakpoint_id)
        
        # Remove breakpoint
        del self._breakpoints[breakpoint_id]
        
        return True
    
    async def enable_breakpoint(self, breakpoint_id: str) -> bool:
        """
        Enable a breakpoint.
        
        Args:
            breakpoint_id: ID of the breakpoint
            
        Returns:
            bool: True if enabled successfully
        """
        if breakpoint_id not in self._breakpoints:
            return False
        
        self._breakpoints[breakpoint_id].enabled = True
        return True
    
    async def disable_breakpoint(self, breakpoint_id: str) -> bool:
        """
        Disable a breakpoint.
        
        Args:
            breakpoint_id: ID of the breakpoint
            
        Returns:
            bool: True if disabled successfully
        """
        if breakpoint_id not in self._breakpoints:
            return False
        
        self._breakpoints[breakpoint_id].enabled = False
        return True
    
    async def get_breakpoint(self, breakpoint_id: str) -> Optional[Breakpoint]:
        """
        Get a breakpoint by ID.
        
        Args:
            breakpoint_id: ID of the breakpoint
            
        Returns:
            Breakpoint or None: The breakpoint if found
        """
        return self._breakpoints.get(breakpoint_id)
    
    async def list_breakpoints(self, session_id: str) -> list[Breakpoint]:
        """
        List all breakpoints for a session.
        
        Args:
            session_id: Debug session ID
            
        Returns:
            list[Breakpoint]: All breakpoints for the session
        """
        breakpoint_ids = self._session_breakpoints.get(session_id, [])
        return [
            self._breakpoints[bp_id]
            for bp_id in breakpoint_ids
            if bp_id in self._breakpoints
        ]
    
    async def check_breakpoint(
        self,
        session_id: str,
        step_number: int,
        tool_name: Optional[str] = None,
        variables: Optional[dict] = None
    ) -> Optional[Breakpoint]:
        """
        Check if execution should break at current point.
        
        Args:
            session_id: Debug session ID
            step_number: Current step number
            tool_name: Current tool name (if any)
            variables: Current variables (for condition evaluation)
            
        Returns:
            Breakpoint or None: The breakpoint if hit, None otherwise
        """
        breakpoints = await self.list_breakpoints(session_id)
        
        for breakpoint in breakpoints:
            if not breakpoint.enabled:
                continue
            
            should_break = False
            
            # Check step breakpoint
            if breakpoint.type == BreakpointType.STEP:
                if breakpoint.step_number == step_number:
                    should_break = True
            
            # Check tool breakpoint
            elif breakpoint.type == BreakpointType.TOOL:
                if breakpoint.tool_name == tool_name:
                    should_break = True
            
            # Check conditional breakpoint
            elif breakpoint.type == BreakpointType.CONDITION:
                if breakpoint.condition and variables:
                    try:
                        # Safe evaluation
                        result = eval(
                            breakpoint.condition,
                            {"__builtins__": {}},
                            variables
                        )
                        if result:
                            should_break = True
                    except:
                        pass
            
            # Error breakpoints are checked elsewhere
            elif breakpoint.type == BreakpointType.ERROR:
                pass
            
            if should_break:
                breakpoint.hit_count += 1
                return breakpoint
        
        return None
    
    async def clear_session_breakpoints(self, session_id: str) -> int:
        """
        Clear all breakpoints for a session.
        
        Args:
            session_id: Debug session ID
            
        Returns:
            int: Number of breakpoints cleared
        """
        if session_id not in self._session_breakpoints:
            return 0
        
        breakpoint_ids = self._session_breakpoints[session_id].copy()
        count = 0
        
        for breakpoint_id in breakpoint_ids:
            if await self.remove_breakpoint(breakpoint_id):
                count += 1
        
        return count
