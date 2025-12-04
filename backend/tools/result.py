"""
ToolResult dataclass for standardized tool outputs.

This module defines the standardized result format that all tools
must return, ensuring consistent handling of tool execution results.
"""

from typing import Any, Optional, Dict, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


def _utcnow():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class ToolResult(BaseModel):
    """
    Standardized result from tool execution.
    
    All tools must return a ToolResult instance to ensure consistent
    handling of success, errors, and metadata across the platform.
    """
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    success: bool = Field(..., description="Whether the tool executed successfully")
    output: Any = Field(None, description="Primary output data from the tool")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about execution")
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="Files or data artifacts produced")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=_utcnow, description="When the result was created")
    
    # Additional context fields
    tool_name: Optional[str] = Field(None, description="Name of the tool that produced this result")
    tool_version: Optional[str] = Field(None, description="Version of the tool")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings during execution")
    
    @classmethod
    def success_result(
        cls,
        output: Any,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "ToolResult":
        """
        Create a successful tool result.
        
        Args:
            output: The output data from the tool
            tool_name: Name of the tool
            metadata: Additional metadata
            **kwargs: Additional fields
            
        Returns:
            ToolResult instance indicating success
        """
        return cls(
            success=True,
            output=output,
            tool_name=tool_name,
            metadata=metadata or {},
            **kwargs
        )
    
    @classmethod
    def error_result(
        cls,
        error: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "ToolResult":
        """
        Create a failed tool result.
        
        Args:
            error: Error message describing the failure
            tool_name: Name of the tool
            metadata: Additional metadata
            **kwargs: Additional fields
            
        Returns:
            ToolResult instance indicating failure
        """
        return cls(
            success=False,
            error=error,
            tool_name=tool_name,
            metadata=metadata or {},
            **kwargs
        )
    
    def add_artifact(
        self,
        artifact_type: str,
        path: Optional[str] = None,
        data: Optional[Any] = None,
        name: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Add an artifact to the result.
        
        Args:
            artifact_type: Type of artifact (e.g., 'file', 'image', 'data')
            path: Path to the artifact file (if applicable)
            data: Inline artifact data (if applicable)
            name: Human-readable name for the artifact
            **metadata: Additional artifact metadata
        """
        artifact = {
            "type": artifact_type,
            "name": name,
            "path": path,
            "data": data,
            **metadata
        }
        self.artifacts.append(artifact)
    
    def add_warning(self, warning: str) -> None:
        """
        Add a warning to the result.
        
        Args:
            warning: Warning message
        """
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation
        """
        return self.model_dump()
    
    def to_json(self) -> str:
        """
        Convert result to JSON string.
        
        Returns:
            JSON string representation
        """
        return self.model_dump_json()
    
    def __str__(self) -> str:
        """String representation of the result."""
        if self.success:
            return f"ToolResult(success=True, output={self.output})"
        else:
            return f"ToolResult(success=False, error={self.error})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ToolResult(success={self.success}, "
            f"tool_name={self.tool_name}, "
            f"output={self.output}, "
            f"error={self.error})"
        )
