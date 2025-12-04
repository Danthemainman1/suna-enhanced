"""Tests for productivity tools."""

import pytest
from unittest.mock import AsyncMock, patch

from tools.productivity.notion import NotionTool
from tools.productivity.trello import TrelloTool
from tools.productivity.todoist import TodoistTool
from tools.exceptions import ToolAuthenticationError


class TestNotionTool:
    """Tests for Notion integration tool."""
    
    def test_notion_tool_init_without_token(self):
        """Test Notion tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            NotionTool()
    
    def test_notion_tool_init_with_token(self):
        """Test Notion tool initialization with token."""
        tool = NotionTool(token="secret_test_token")
        assert tool.name == "notion"
        assert tool.token == "secret_test_token"
    
    def test_notion_tool_capabilities(self):
        """Test Notion tool capabilities."""
        tool = NotionTool(token="secret_test_token")
        capabilities = tool.get_capabilities()
        assert "page_management" in capabilities
        assert "database_management" in capabilities
        assert "search" in capabilities
    
    @pytest.mark.asyncio
    async def test_notion_create_page(self):
        """Test Notion create page."""
        tool = NotionTool(token="secret_test_token")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": "page_123",
                "url": "https://notion.so/page_123"
            }
            
            result = await tool.create_page(
                parent_id="parent_123",
                title="Test Page"
            )
            
            assert result.success is True
            assert result.output["page_id"] == "page_123"
    
    @pytest.mark.asyncio
    async def test_notion_search(self):
        """Test Notion search."""
        tool = NotionTool(token="secret_test_token")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "results": [{"id": "1"}, {"id": "2"}]
            }
            
            result = await tool.search(query="test")
            
            assert result.success is True
            assert len(result.output) == 2


class TestTrelloTool:
    """Tests for Trello integration tool."""
    
    def test_trello_tool_init_without_credentials(self):
        """Test Trello tool initialization fails without credentials."""
        with pytest.raises(ToolAuthenticationError):
            TrelloTool()
    
    def test_trello_tool_init_with_credentials(self):
        """Test Trello tool initialization with credentials."""
        tool = TrelloTool(api_key="key123", token="token123")
        assert tool.name == "trello"
        assert tool.api_key == "key123"


class TestTodoistTool:
    """Tests for Todoist integration tool."""
    
    def test_todoist_tool_init_without_token(self):
        """Test Todoist tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            TodoistTool()
    
    def test_todoist_tool_init_with_token(self):
        """Test Todoist tool initialization with token."""
        tool = TodoistTool(api_token="token123")
        assert tool.name == "todoist"
        assert tool.api_token == "token123"
