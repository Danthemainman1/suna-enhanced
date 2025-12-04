"""
Custom exceptions for tool system.

This module defines custom exception classes used throughout the tool ecosystem
for standardized error handling.
"""

from typing import Optional, Dict, Any


class ToolException(Exception):
    """Base exception for all tool-related errors."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool exception.
        
        Args:
            message: Error message
            tool_name: Name of the tool that raised the error
            metadata: Additional error metadata
        """
        super().__init__(message)
        self.message = message
        self.tool_name = tool_name
        self.metadata = metadata or {}


class ToolExecutionError(ToolException):
    """Raised when tool execution fails."""
    pass


class ToolValidationError(ToolException):
    """Raised when tool input validation fails."""
    pass


class ToolAuthenticationError(ToolException):
    """Raised when tool authentication fails."""
    pass


class ToolConfigurationError(ToolException):
    """Raised when tool configuration is invalid."""
    pass


class ToolTimeoutError(ToolException):
    """Raised when tool execution times out."""
    pass


class ToolRateLimitError(ToolException):
    """Raised when tool hits rate limit."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            tool_name: Name of the tool
            retry_after: Seconds to wait before retry
            metadata: Additional error metadata
        """
        super().__init__(message, tool_name, metadata)
        self.retry_after = retry_after


class ToolNotFoundError(ToolException):
    """Raised when requested tool is not found in registry."""
    pass


class ToolRegistrationError(ToolException):
    """Raised when tool registration fails."""
    pass
