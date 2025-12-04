"""Integration tests for tool registry."""

import pytest

from tools.registry import ToolRegistry, get_registry, reset_registry
from tools.communication.slack import SlackTool
from tools.development.github_tool import GitHubTool
from tools.productivity.notion import NotionTool


class TestToolRegistry:
    """Tests for tool registry."""
    
    def setup_method(self):
        """Reset registry before each test."""
        reset_registry()
    
    def test_registry_singleton(self):
        """Test registry is a singleton."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = get_registry()
        tool = SlackTool(token="test-token")
        
        result = registry.register(tool)
        assert result is True
        assert registry.has_tool("slack")
        assert registry.count() == 1
    
    def test_register_duplicate_tool(self):
        """Test registering duplicate tool fails."""
        registry = get_registry()
        tool1 = SlackTool(token="test-token-1")
        tool2 = SlackTool(token="test-token-2")
        
        registry.register(tool1)
        result = registry.register(tool2, replace=False)
        
        assert result is False
        assert registry.count() == 1
    
    def test_replace_tool(self):
        """Test replacing a tool."""
        registry = get_registry()
        tool1 = SlackTool(token="test-token-1")
        tool2 = SlackTool(token="test-token-2")
        
        registry.register(tool1)
        result = registry.register(tool2, replace=True)
        
        assert result is True
        assert registry.count() == 1
        assert registry.get("slack").token == "test-token-2"
    
    def test_get_tool(self):
        """Test getting a tool from registry."""
        registry = get_registry()
        tool = SlackTool(token="test-token")
        registry.register(tool)
        
        retrieved = registry.get("slack")
        assert retrieved is not None
        assert retrieved.name == "slack"
    
    def test_list_tools(self):
        """Test listing all tools."""
        registry = get_registry()
        
        slack = SlackTool(token="test-token")
        github = GitHubTool(token="test-token")
        notion = NotionTool(token="test-token")
        
        registry.register(slack)
        registry.register(github)
        registry.register(notion)
        
        tools = registry.list_tools()
        assert len(tools) == 3
        assert "slack" in tools
        assert "github" in tools
        assert "notion" in tools
    
    def test_get_tools_by_category(self):
        """Test filtering tools by category."""
        registry = get_registry()
        
        slack = SlackTool(token="test-token")
        github = GitHubTool(token="test-token")
        
        registry.register(slack)
        registry.register(github)
        
        comm_tools = registry.get_tools_by_category("communication")
        assert len(comm_tools) == 1
        assert comm_tools[0].name == "slack"
        
        dev_tools = registry.get_tools_by_category("development")
        assert len(dev_tools) == 1
        assert dev_tools[0].name == "github"
    
    def test_get_tools_by_capability(self):
        """Test filtering tools by capability."""
        registry = get_registry()
        
        slack = SlackTool(token="test-token")
        github = GitHubTool(token="test-token")
        
        registry.register(slack)
        registry.register(github)
        
        messaging_tools = registry.get_tools_by_capability("messaging")
        assert len(messaging_tools) == 1
        assert messaging_tools[0].name == "slack"
    
    def test_search_tools(self):
        """Test searching tools."""
        registry = get_registry()
        
        slack = SlackTool(token="test-token")
        github = GitHubTool(token="test-token")
        
        registry.register(slack)
        registry.register(github)
        
        results = registry.search("slack")
        assert len(results) == 1
        assert results[0].name == "slack"
        
        results = registry.search("manage")
        assert len(results) >= 1  # Should match multiple tools with "manage" in description
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = get_registry()
        tool = SlackTool(token="test-token")
        
        registry.register(tool)
        assert registry.count() == 1
        
        result = registry.unregister("slack")
        assert result is True
        assert registry.count() == 0
        assert not registry.has_tool("slack")
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = get_registry()
        
        slack = SlackTool(token="test-token")
        github = GitHubTool(token="test-token")
        
        registry.register(slack)
        registry.register(github)
        assert registry.count() == 2
        
        registry.clear()
        assert registry.count() == 0
