"""
Base Tool class for all tools in Suna Ultra.

This module defines the abstract base class that all tools must inherit from,
ensuring consistent behavior and interface across the tool ecosystem.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
import time
import logging

from .result import ToolResult


logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, int, bool, etc.)")
    description: str = Field(..., description="Description of the parameter")
    required: bool = Field(True, description="Whether the parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    enum: Optional[List[Any]] = Field(None, description="Allowed values (if constrained)")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class ToolMetadata(BaseModel):
    """Metadata about a tool."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    version: str = Field("1.0.0", description="Tool version")
    author: Optional[str] = Field(None, description="Tool author")
    category: Optional[str] = Field(None, description="Tool category")
    tags: List[str] = Field(default_factory=list, description="Tags for searching/filtering")
    capabilities: List[str] = Field(default_factory=list, description="Tool capabilities")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    requires_auth: bool = Field(False, description="Whether tool requires authentication")
    is_async: bool = Field(True, description="Whether tool supports async execution")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class Tool(ABC):
    """
    Abstract base class for all tools.
    
    All tools in Suna Ultra must inherit from this class and implement
    the required abstract methods to ensure consistent behavior.
    
    Example:
        ```python
        class MyTool(Tool):
            name = "my_tool"
            description = "Does something useful"
            
            async def execute(self, **kwargs) -> ToolResult:
                # Tool implementation
                result = do_something(kwargs)
                return ToolResult.success_result(result, tool_name=self.name)
            
            def validate_input(self, **kwargs) -> bool:
                return "required_param" in kwargs
            
            def get_capabilities(self) -> list[str]:
                return ["capability1", "capability2"]
        ```
    """
    
    # Class attributes that subclasses must define
    name: str = "base_tool"
    description: str = "Base tool class"
    version: str = "1.0.0"
    category: Optional[str] = None
    
    def __init__(self, **config):
        """
        Initialize the tool with configuration.
        
        Args:
            **config: Tool-specific configuration options
        """
        self.config = config
        self._metadata: Optional[ToolMetadata] = None
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        This is the main method that performs the tool's functionality.
        All implementations must be async and return a ToolResult.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution results
            
        Raises:
            Exception: If execution fails (should be caught and returned as error result)
        """
        pass
    
    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters before execution.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Get list of capabilities this tool provides.
        
        Capabilities are used for tool discovery and selection.
        Examples: ["web_search", "file_read", "code_execution"]
        
        Returns:
            List of capability identifiers
        """
        pass
    
    def get_metadata(self) -> ToolMetadata:
        """
        Get tool metadata.
        
        Returns:
            ToolMetadata instance
        """
        if self._metadata is None:
            self._metadata = ToolMetadata(
                name=self.name,
                description=self.description,
                version=self.version,
                category=self.category,
                capabilities=self.get_capabilities(),
                parameters=self.get_parameters()
            )
        return self._metadata
    
    def get_parameters(self) -> List[ToolParameter]:
        """
        Get list of tool parameters.
        
        Subclasses can override this to provide parameter definitions.
        
        Returns:
            List of ToolParameter instances
        """
        return []
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with error handling and timing.
        
        This method wraps execute() with validation, error handling,
        and execution time tracking.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution results or error
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not self.validate_input(**kwargs):
                return ToolResult.error_result(
                    error="Input validation failed",
                    tool_name=self.name,
                    metadata={"parameters": kwargs}
                )
            
            # Execute tool
            result = await self.execute(**kwargs)
            
            # Add execution metadata
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.tool_name = self.name
            result.tool_version = self.version
            
            return result
            
        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {e}", exc_info=True)
            execution_time = time.time() - start_time
            
            return ToolResult.error_result(
                error=str(e),
                tool_name=self.name,
                execution_time=execution_time,
                metadata={
                    "exception_type": type(e).__name__,
                    "parameters": kwargs
                }
            )
    
    def supports_capability(self, capability: str) -> bool:
        """
        Check if tool supports a specific capability.
        
        Args:
            capability: Capability identifier
            
        Returns:
            True if capability is supported
        """
        return capability in self.get_capabilities()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name} (v{self.version})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Tool(name={self.name}, version={self.version}, category={self.category})"


class BaseTool(Tool):
    """
    Concrete base tool with common functionality.
    
    Provides default implementations for common tool patterns.
    Subclasses can override specific methods as needed.
    """
    
    def validate_input(self, **kwargs) -> bool:
        """
        Default input validation.
        
        Validates that all required parameters are present.
        """
        parameters = self.get_parameters()
        
        for param in parameters:
            if param.required and param.name not in kwargs:
                logger.warning(f"Required parameter '{param.name}' missing for tool {self.name}")
                return False
            
            # Check enum constraints
            if param.enum and param.name in kwargs:
                if kwargs[param.name] not in param.enum:
                    logger.warning(
                        f"Parameter '{param.name}' value '{kwargs[param.name]}' "
                        f"not in allowed values: {param.enum}"
                    )
                    return False
        
        return True
    
    def get_capabilities(self) -> list[str]:
        """
        Default capabilities.
        
        Returns the tool's category as its primary capability.
        """
        if self.category:
            return [self.category]
        return []
