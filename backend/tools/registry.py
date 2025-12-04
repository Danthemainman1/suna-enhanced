"""
Tool registry for discovering and managing tools.

This module provides a centralized registry for all available tools,
enabling discovery, filtering, and version management.
"""

from typing import Dict, List, Optional, Type, Set
import logging
from collections import defaultdict

from .base import Tool, ToolMetadata


logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing tools.
    
    Features:
    - Register and unregister tools
    - Get tool by name
    - List all available tools
    - Filter tools by capability
    - Tool versioning support
    - Category-based organization
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Tool] = {}
        self._tool_classes: Dict[str, Type[Tool]] = {}
        self._versions: Dict[str, List[str]] = defaultdict(list)
        self._capabilities_index: Dict[str, Set[str]] = defaultdict(set)
        self._category_index: Dict[str, Set[str]] = defaultdict(set)
        self._tags_index: Dict[str, Set[str]] = defaultdict(set)
    
    def register(
        self,
        tool: Tool,
        replace: bool = False
    ) -> bool:
        """
        Register a tool instance.
        
        Args:
            tool: Tool instance to register
            replace: Whether to replace existing tool with same name
            
        Returns:
            True if registered successfully, False if tool already exists
        """
        tool_name = tool.name
        
        # Check if tool already exists
        if tool_name in self._tools and not replace:
            logger.warning(f"Tool '{tool_name}' already registered")
            return False
        
        # Register tool
        self._tools[tool_name] = tool
        self._tool_classes[tool_name] = type(tool)
        
        # Track version
        if tool.version not in self._versions[tool_name]:
            self._versions[tool_name].append(tool.version)
        
        # Index capabilities
        for capability in tool.get_capabilities():
            self._capabilities_index[capability].add(tool_name)
        
        # Index category
        if tool.category:
            self._category_index[tool.category].add(tool_name)
        
        # Index tags
        metadata = tool.get_metadata()
        for tag in metadata.tags:
            self._tags_index[tag].add(tool_name)
        
        logger.info(f"Registered tool: {tool_name} (v{tool.version})")
        return True
    
    def register_class(
        self,
        tool_class: Type[Tool],
        **config
    ) -> bool:
        """
        Register a tool class (will instantiate it).
        
        Args:
            tool_class: Tool class to register
            **config: Configuration for tool instantiation
            
        Returns:
            True if registered successfully
        """
        try:
            tool_instance = tool_class(**config)
            return self.register(tool_instance)
        except Exception as e:
            logger.error(f"Failed to instantiate tool {tool_class.__name__}: {e}")
            return False
    
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistered successfully, False if tool not found
        """
        if tool_name not in self._tools:
            logger.warning(f"Tool '{tool_name}' not found in registry")
            return False
        
        tool = self._tools[tool_name]
        
        # Remove from indexes
        for capability in tool.get_capabilities():
            self._capabilities_index[capability].discard(tool_name)
        
        if tool.category:
            self._category_index[tool.category].discard(tool_name)
        
        metadata = tool.get_metadata()
        for tag in metadata.tags:
            self._tags_index[tag].discard(tool_name)
        
        # Remove from main registry
        del self._tools[tool_name]
        del self._tool_classes[tool_name]
        
        logger.info(f"Unregistered tool: {tool_name}")
        return True
    
    def get(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_class(self, tool_name: str) -> Optional[Type[Tool]]:
        """
        Get a tool class by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool class or None if not found
        """
        return self._tool_classes.get(tool_name)
    
    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool is registered
        """
        return tool_name in self._tools
    
    def list_tools(
        self,
        category: Optional[str] = None,
        capability: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[str]:
        """
        List all registered tools with optional filtering.
        
        Args:
            category: Filter by category
            capability: Filter by capability
            tag: Filter by tag
            
        Returns:
            List of tool names
        """
        tools = set(self._tools.keys())
        
        # Apply filters
        if category:
            tools = tools.intersection(self._category_index.get(category, set()))
        
        if capability:
            tools = tools.intersection(self._capabilities_index.get(capability, set()))
        
        if tag:
            tools = tools.intersection(self._tags_index.get(tag, set()))
        
        return sorted(list(tools))
    
    def get_tools_by_capability(self, capability: str) -> List[Tool]:
        """
        Get all tools that support a specific capability.
        
        Args:
            capability: Capability identifier
            
        Returns:
            List of Tool instances
        """
        tool_names = self._capabilities_index.get(capability, set())
        return [self._tools[name] for name in tool_names]
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of Tool instances
        """
        tool_names = self._category_index.get(category, set())
        return [self._tools[name] for name in tool_names]
    
    def get_tools_by_tag(self, tag: str) -> List[Tool]:
        """
        Get all tools with a specific tag.
        
        Args:
            tag: Tag name
            
        Returns:
            List of Tool instances
        """
        tool_names = self._tags_index.get(tag, set())
        return [self._tools[name] for name in tool_names]
    
    def get_all_capabilities(self) -> List[str]:
        """
        Get all available capabilities across all tools.
        
        Returns:
            List of capability identifiers
        """
        return sorted(list(self._capabilities_index.keys()))
    
    def get_all_categories(self) -> List[str]:
        """
        Get all tool categories.
        
        Returns:
            List of category names
        """
        return sorted(list(self._category_index.keys()))
    
    def get_all_tags(self) -> List[str]:
        """
        Get all tool tags.
        
        Returns:
            List of tag names
        """
        return sorted(list(self._tags_index.keys()))
    
    def get_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """
        Get metadata for a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolMetadata or None if tool not found
        """
        tool = self.get(tool_name)
        if tool:
            return tool.get_metadata()
        return None
    
    def get_all_metadata(self) -> List[ToolMetadata]:
        """
        Get metadata for all registered tools.
        
        Returns:
            List of ToolMetadata instances
        """
        return [tool.get_metadata() for tool in self._tools.values()]
    
    def get_versions(self, tool_name: str) -> List[str]:
        """
        Get all registered versions of a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            List of version strings
        """
        return self._versions.get(tool_name, [])
    
    def search(
        self,
        query: str,
        search_in: List[str] = None
    ) -> List[Tool]:
        """
        Search for tools by keyword.
        
        Args:
            query: Search query
            search_in: Fields to search in (name, description, capabilities, tags)
            
        Returns:
            List of matching Tool instances
        """
        if search_in is None:
            search_in = ["name", "description", "capabilities", "tags"]
        
        query_lower = query.lower()
        results = []
        
        for tool in self._tools.values():
            metadata = tool.get_metadata()
            match = False
            
            # Search in name
            if "name" in search_in and query_lower in metadata.name.lower():
                match = True
            
            # Search in description
            if "description" in search_in and query_lower in metadata.description.lower():
                match = True
            
            # Search in capabilities
            if "capabilities" in search_in:
                if any(query_lower in cap.lower() for cap in metadata.capabilities):
                    match = True
            
            # Search in tags
            if "tags" in search_in:
                if any(query_lower in tag.lower() for tag in metadata.tags):
                    match = True
            
            if match:
                results.append(tool)
        
        return results
    
    def count(self) -> int:
        """
        Get total number of registered tools.
        
        Returns:
            Number of tools
        """
        return len(self._tools)
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._tool_classes.clear()
        self._versions.clear()
        self._capabilities_index.clear()
        self._category_index.clear()
        self._tags_index.clear()
        logger.info("Tool registry cleared")
    
    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if tool is registered."""
        return tool_name in self._tools
    
    def __iter__(self):
        """Iterate over registered tools."""
        return iter(self._tools.values())
    
    def __str__(self) -> str:
        """String representation."""
        return f"ToolRegistry({len(self._tools)} tools)"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ToolRegistry(tools={list(self._tools.keys())})"


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        ToolRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def reset_registry() -> ToolRegistry:
    """
    Reset the global tool registry.
    
    Returns:
        New ToolRegistry instance
    """
    global _global_registry
    _global_registry = ToolRegistry()
    return _global_registry
