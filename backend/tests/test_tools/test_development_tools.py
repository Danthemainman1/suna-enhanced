"""Tests for development tools."""

import pytest
from unittest.mock import AsyncMock, patch

from tools.development.github_tool import GitHubTool
from tools.development.jira import JiraTool
from tools.exceptions import ToolAuthenticationError


class TestGitHubTool:
    """Tests for GitHub integration tool."""
    
    def test_github_tool_init_without_token(self):
        """Test GitHub tool initialization fails without token."""
        with pytest.raises(ToolAuthenticationError):
            GitHubTool()
    
    def test_github_tool_init_with_token(self):
        """Test GitHub tool initialization with token."""
        tool = GitHubTool(token="ghp_test_token")
        assert tool.name == "github"
        assert tool.token == "ghp_test_token"
    
    def test_github_tool_capabilities(self):
        """Test GitHub tool capabilities."""
        tool = GitHubTool(token="ghp_test_token")
        capabilities = tool.get_capabilities()
        assert "repo_management" in capabilities
        assert "issue_management" in capabilities
        assert "pr_management" in capabilities
    
    @pytest.mark.asyncio
    async def test_github_create_repo(self):
        """Test GitHub create repository."""
        tool = GitHubTool(token="ghp_test_token")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "id": 123456,
                "html_url": "https://github.com/user/repo"
            }
            
            result = await tool.create_repo(
                name="test-repo",
                private=True,
                description="Test repository"
            )
            
            assert result.success is True
            assert result.output["repo_id"] == 123456
    
    @pytest.mark.asyncio
    async def test_github_create_issue(self):
        """Test GitHub create issue."""
        tool = GitHubTool(token="ghp_test_token")
        
        with patch.object(tool, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {
                "number": 42,
                "html_url": "https://github.com/user/repo/issues/42"
            }
            
            result = await tool.create_issue(
                owner="user",
                repo="repo",
                title="Test Issue",
                body="Test body"
            )
            
            assert result.success is True
            assert result.output["issue_number"] == 42


class TestJiraTool:
    """Tests for Jira integration tool."""
    
    def test_jira_tool_init_without_credentials(self):
        """Test Jira tool initialization fails without credentials."""
        with pytest.raises(ToolAuthenticationError):
            JiraTool()
    
    def test_jira_tool_init_with_credentials(self):
        """Test Jira tool initialization with credentials."""
        tool = JiraTool(
            api_token="token123",
            email="user@example.com",
            domain="example.atlassian.net"
        )
        assert tool.name == "jira"
        assert tool.api_token == "token123"
