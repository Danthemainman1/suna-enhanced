"""
Tool infrastructure for Suna Ultra.

This module provides the base classes and registry for the tool system,
enabling extensible tool development and management.

Key Features:
- Abstract base Tool class for consistent interface
- Standardized ToolResult for all tool outputs
- Central ToolRegistry for tool discovery and management
- Support for tool capabilities, categories, and versioning
- Async/await for all tool operations
"""

from .base import Tool, BaseTool, ToolParameter, ToolMetadata
from .result import ToolResult
from .registry import ToolRegistry, get_registry, reset_registry


__all__ = [
    # Base classes
    "Tool",
    "BaseTool",
    "ToolParameter",
    "ToolMetadata",
    
    # Result
    "ToolResult",
    
    # Registry
    "ToolRegistry",
    "get_registry",
    "reset_registry",
]


__version__ = "1.0.0"
