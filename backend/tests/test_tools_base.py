"""
Tests for tool base classes and registry.

This module tests the tool infrastructure including base classes,
ToolResult, and the ToolRegistry.
"""

import pytest
from datetime import datetime

from tools.base import Tool, BaseTool, ToolParameter, ToolMetadata
from tools.result import ToolResult
from tools.registry import ToolRegistry, get_registry, reset_registry


class TestToolResult:
    """Tests for ToolResult dataclass."""
    
    def test_success_result(self):
        """Test creating a success result."""
        result = ToolResult.success_result(
            output="test output",
            tool_name="test_tool"
        )
        
        assert result.success is True
        assert result.output == "test output"
        assert result.tool_name == "test_tool"
        assert result.error is None
    
    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult.error_result(
            error="test error",
            tool_name="test_tool"
        )
        
        assert result.success is False
        assert result.error == "test error"
        assert result.tool_name == "test_tool"
        assert result.output is None
    
    def test_add_artifact(self):
        """Test adding artifacts to result."""
        result = ToolResult.success_result(output="test")
        
        result.add_artifact(
            artifact_type="file",
            path="/tmp/test.txt",
            name="test file"
        )
        
        assert len(result.artifacts) == 1
        assert result.artifacts[0]["type"] == "file"
        assert result.artifacts[0]["path"] == "/tmp/test.txt"
        assert result.artifacts[0]["name"] == "test file"
    
    def test_add_warning(self):
        """Test adding warnings to result."""
        result = ToolResult.success_result(output="test")
        
        result.add_warning("test warning")
        
        assert len(result.warnings) == 1
        assert result.warnings[0] == "test warning"
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ToolResult.success_result(
            output="test",
            tool_name="test_tool"
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["success"] is True
        assert result_dict["output"] == "test"
        assert result_dict["tool_name"] == "test_tool"
    
    def test_str_representation(self):
        """Test string representation."""
        result = ToolResult.success_result(output="test")
        str_repr = str(result)
        
        assert "ToolResult" in str_repr
        assert "success=True" in str_repr


class TestTool:
    """Tests for base Tool class."""
    
    def test_tool_abstract(self):
        """Test that Tool cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Tool()
    
    @pytest.mark.asyncio
    async def test_concrete_tool(self, sample_tool):
        """Test concrete tool implementation."""
        assert sample_tool.name == "test_tool"
        assert sample_tool.description == "A test tool"
        assert sample_tool.version == "1.0.0"
        
        result = await sample_tool.execute(test_param="value")
        assert result.success is True
        assert result.output["result"] == "value"
    
    @pytest.mark.asyncio
    async def test_safe_execute_success(self, sample_tool):
        """Test safe_execute with successful execution."""
        result = await sample_tool.safe_execute(test_param="value")
        
        assert result.success is True
        assert result.execution_time is not None
        assert result.tool_name == "test_tool"
        assert result.tool_version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_safe_execute_with_exception(self):
        """Test safe_execute with exception."""
        class FailingTool(Tool):
            name = "failing_tool"
            description = "A tool that fails"
            version = "1.0.0"
            
            async def execute(self, **kwargs) -> ToolResult:
                raise ValueError("Test error")
            
            def validate_input(self, **kwargs) -> bool:
                return True
            
            def get_capabilities(self) -> list[str]:
                return []
        
        tool = FailingTool()
        result = await tool.safe_execute()
        
        assert result.success is False
        assert "Test error" in result.error
        assert result.execution_time is not None
    
    def test_get_metadata(self, sample_tool):
        """Test getting tool metadata."""
        metadata = sample_tool.get_metadata()
        
        assert isinstance(metadata, ToolMetadata)
        assert metadata.name == "test_tool"
        assert metadata.description == "A test tool"
        assert metadata.version == "1.0.0"
        assert "test_capability" in metadata.capabilities
    
    def test_supports_capability(self, sample_tool):
        """Test checking capability support."""
        assert sample_tool.supports_capability("test_capability") is True
        assert sample_tool.supports_capability("unknown_capability") is False


class TestBaseTool:
    """Tests for BaseTool class."""
    
    def test_validate_input_with_parameters(self):
        """Test input validation with parameters."""
        class ParameterizedTool(BaseTool):
            name = "param_tool"
            description = "Tool with parameters"
            version = "1.0.0"
            
            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult.success_result(output="test")
            
            def get_parameters(self):
                return [
                    ToolParameter(
                        name="required_param",
                        type="string",
                        description="A required parameter",
                        required=True
                    ),
                    ToolParameter(
                        name="optional_param",
                        type="string",
                        description="An optional parameter",
                        required=False
                    )
                ]
        
        tool = ParameterizedTool()
        
        # Should fail without required param
        assert tool.validate_input() is False
        
        # Should succeed with required param
        assert tool.validate_input(required_param="value") is True
        
        # Should succeed with both params
        assert tool.validate_input(
            required_param="value",
            optional_param="other"
        ) is True
    
    def test_validate_input_with_enum(self):
        """Test input validation with enum constraints."""
        class EnumTool(BaseTool):
            name = "enum_tool"
            description = "Tool with enum parameter"
            version = "1.0.0"
            
            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult.success_result(output="test")
            
            def get_parameters(self):
                return [
                    ToolParameter(
                        name="choice",
                        type="string",
                        description="A choice parameter",
                        required=True,
                        enum=["option1", "option2", "option3"]
                    )
                ]
        
        tool = EnumTool()
        
        # Should succeed with valid enum value
        assert tool.validate_input(choice="option1") is True
        
        # Should fail with invalid enum value
        assert tool.validate_input(choice="invalid") is False


class TestToolRegistry:
    """Tests for ToolRegistry."""
    
    def test_register_tool(self, tool_registry, sample_tool):
        """Test registering a tool."""
        result = tool_registry.register(sample_tool)
        
        assert result is True
        assert tool_registry.has_tool("test_tool")
    
    def test_register_duplicate(self, tool_registry, sample_tool):
        """Test registering duplicate tool."""
        tool_registry.register(sample_tool)
        result = tool_registry.register(sample_tool, replace=False)
        
        assert result is False
    
    def test_register_duplicate_with_replace(self, tool_registry, sample_tool):
        """Test registering duplicate with replace flag."""
        tool_registry.register(sample_tool)
        result = tool_registry.register(sample_tool, replace=True)
        
        assert result is True
    
    def test_get_tool(self, tool_registry, sample_tool):
        """Test getting a tool by name."""
        tool_registry.register(sample_tool)
        
        retrieved = tool_registry.get("test_tool")
        assert retrieved is not None
        assert retrieved.name == "test_tool"
    
    def test_get_nonexistent_tool(self, tool_registry):
        """Test getting a non-existent tool."""
        result = tool_registry.get("nonexistent")
        assert result is None
    
    def test_unregister_tool(self, tool_registry, sample_tool):
        """Test unregistering a tool."""
        tool_registry.register(sample_tool)
        result = tool_registry.unregister("test_tool")
        
        assert result is True
        assert not tool_registry.has_tool("test_tool")
    
    def test_list_tools(self, tool_registry, sample_tool):
        """Test listing all tools."""
        tool_registry.register(sample_tool)
        
        tools = tool_registry.list_tools()
        assert "test_tool" in tools
    
    def test_get_tools_by_capability(self, tool_registry, sample_tool):
        """Test filtering tools by capability."""
        tool_registry.register(sample_tool)
        
        tools = tool_registry.get_tools_by_capability("test_capability")
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
    
    def test_get_tools_by_category(self, tool_registry, sample_tool):
        """Test filtering tools by category."""
        tool_registry.register(sample_tool)
        
        tools = tool_registry.get_tools_by_category("testing")
        assert len(tools) == 1
        assert tools[0].name == "test_tool"
    
    def test_get_all_capabilities(self, tool_registry, sample_tool):
        """Test getting all capabilities."""
        tool_registry.register(sample_tool)
        
        capabilities = tool_registry.get_all_capabilities()
        assert "test_capability" in capabilities
    
    def test_get_all_categories(self, tool_registry, sample_tool):
        """Test getting all categories."""
        tool_registry.register(sample_tool)
        
        categories = tool_registry.get_all_categories()
        assert "testing" in categories
    
    def test_search_tools(self, tool_registry, sample_tool):
        """Test searching for tools."""
        tool_registry.register(sample_tool)
        
        # Search by name
        results = tool_registry.search("test")
        assert len(results) == 1
        assert results[0].name == "test_tool"
        
        # Search by capability
        results = tool_registry.search("test_capability")
        assert len(results) == 1
    
    def test_count(self, tool_registry, sample_tool):
        """Test counting registered tools."""
        assert tool_registry.count() == 0
        
        tool_registry.register(sample_tool)
        assert tool_registry.count() == 1
    
    def test_clear(self, tool_registry, sample_tool):
        """Test clearing the registry."""
        tool_registry.register(sample_tool)
        tool_registry.clear()
        
        assert tool_registry.count() == 0
    
    def test_len(self, tool_registry, sample_tool):
        """Test len() on registry."""
        tool_registry.register(sample_tool)
        assert len(tool_registry) == 1
    
    def test_contains(self, tool_registry, sample_tool):
        """Test 'in' operator on registry."""
        tool_registry.register(sample_tool)
        assert "test_tool" in tool_registry
        assert "nonexistent" not in tool_registry
    
    def test_iter(self, tool_registry, sample_tool):
        """Test iterating over registry."""
        tool_registry.register(sample_tool)
        
        tools = list(tool_registry)
        assert len(tools) == 1
        assert tools[0].name == "test_tool"


class TestGlobalRegistry:
    """Tests for global registry functions."""
    
    def test_get_registry(self):
        """Test getting global registry."""
        registry = get_registry()
        assert isinstance(registry, ToolRegistry)
    
    def test_get_registry_singleton(self):
        """Test that get_registry returns same instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2
    
    def test_reset_registry(self):
        """Test resetting global registry."""
        registry1 = get_registry()
        registry2 = reset_registry()
        
        assert isinstance(registry2, ToolRegistry)
        assert registry1 is not registry2
