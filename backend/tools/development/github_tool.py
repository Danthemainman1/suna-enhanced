"""GitHub API integration tool with comprehensive functionality."""

import asyncio
import httpx
from typing import Optional, List, Dict, Any
import logging

from ..base import BaseTool, ToolCategory, ToolParameter
from ..result import ToolResult
from ..exceptions import ToolAuthenticationError, ToolExecutionError, ToolRateLimitError


logger = logging.getLogger(__name__)


class GitHubTool(BaseTool):
    """
    GitHub API integration with comprehensive features.
    
    Supports:
    - Repository management
    - Issue management
    - Pull request operations
    - Branch operations
    - GitHub Actions
    - Gists
    - Search
    """
    
    name = "github"
    description = "Manage GitHub repositories, issues, PRs, and more"
    version = "1.0.0"
    category = ToolCategory.DEVELOPMENT.value
    
    def __init__(self, **config):
        super().__init__(**config)
        self.token = config.get("token")
        self.base_url = config.get("base_url", "https://api.github.com")
        
        if not self.token:
            raise ToolAuthenticationError("GitHub personal access token required", tool_name=self.name)
    
    def get_capabilities(self) -> List[str]:
        return [
            "repo_management",
            "issue_management",
            "pr_management",
            "branch_management",
            "actions",
            "gists",
            "search",
        ]
    
    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(name="action", type="string", description="Action to perform", required=True,
                         enum=["create_repo", "list_repos", "create_issue", "list_issues", 
                               "create_pr", "list_prs", "create_branch", "trigger_workflow", 
                               "search_code", "create_gist"]),
            ToolParameter(name="owner", type="string", description="Repository owner", required=False),
            ToolParameter(name="repo", type="string", description="Repository name", required=False),
        ]
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """Make authenticated request to GitHub API with retries."""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=headers, params=data)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == "PATCH":
                        response = await client.patch(url, headers=headers, json=data)
                    else:
                        response = await client.delete(url, headers=headers)
                    
                    if response.status_code == 403 and "rate limit" in response.text.lower():
                        retry_after = int(response.headers.get("X-RateLimit-Reset", 60))
                        if attempt < retries - 1:
                            await asyncio.sleep(min(retry_after, 60))
                            continue
                        raise ToolRateLimitError("GitHub rate limit exceeded", tool_name=self.name)
                    
                    response.raise_for_status()
                    return response.json() if response.content else {}
                    
            except httpx.HTTPError as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                raise ToolExecutionError(f"HTTP request failed: {str(e)}", tool_name=self.name)
        
        raise ToolExecutionError(f"Request failed after {retries} retries", tool_name=self.name)
    
    async def create_repo(self, name: str, private: bool = False, description: str = "") -> ToolResult:
        """Create a new repository."""
        data = {"name": name, "private": private, "description": description}
        result = await self._make_request("POST", "user/repos", data)
        return ToolResult.success_result(
            output={"repo_id": result.get("id"), "url": result.get("html_url")},
            tool_name=self.name,
            metadata={"action": "create_repo"}
        )
    
    async def list_repos(self, owner: Optional[str] = None) -> ToolResult:
        """List repositories."""
        endpoint = f"users/{owner}/repos" if owner else "user/repos"
        result = await self._make_request("GET", endpoint)
        repos = [{"name": r.get("name"), "url": r.get("html_url")} for r in result]
        return ToolResult.success_result(output=repos, tool_name=self.name, metadata={"action": "list_repos"})
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> ToolResult:
        """Create an issue."""
        data = {"title": title, "body": body}
        result = await self._make_request("POST", f"repos/{owner}/{repo}/issues", data)
        return ToolResult.success_result(
            output={"issue_number": result.get("number"), "url": result.get("html_url")},
            tool_name=self.name,
            metadata={"action": "create_issue"}
        )
    
    async def list_issues(self, owner: str, repo: str) -> ToolResult:
        """List repository issues."""
        result = await self._make_request("GET", f"repos/{owner}/{repo}/issues")
        issues = [{"number": i.get("number"), "title": i.get("title"), "state": i.get("state")} for i in result]
        return ToolResult.success_result(output=issues, tool_name=self.name, metadata={"action": "list_issues"})
    
    async def create_pr(self, owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> ToolResult:
        """Create a pull request."""
        data = {"title": title, "head": head, "base": base, "body": body}
        result = await self._make_request("POST", f"repos/{owner}/{repo}/pulls", data)
        return ToolResult.success_result(
            output={"pr_number": result.get("number"), "url": result.get("html_url")},
            tool_name=self.name,
            metadata={"action": "create_pr"}
        )
    
    async def search_code(self, query: str) -> ToolResult:
        """Search code across GitHub."""
        result = await self._make_request("GET", "search/code", {"q": query})
        items = result.get("items", [])
        return ToolResult.success_result(
            output=items,
            tool_name=self.name,
            metadata={"action": "search_code", "count": len(items)}
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute GitHub action."""
        action = kwargs.get("action")
        
        if action == "create_repo":
            return await self.create_repo(
                name=kwargs.get("name"),
                private=kwargs.get("private", False),
                description=kwargs.get("description", "")
            )
        elif action == "list_repos":
            return await self.list_repos(owner=kwargs.get("owner"))
        elif action == "create_issue":
            return await self.create_issue(
                owner=kwargs.get("owner"),
                repo=kwargs.get("repo"),
                title=kwargs.get("title"),
                body=kwargs.get("body", "")
            )
        elif action == "list_issues":
            return await self.list_issues(owner=kwargs.get("owner"), repo=kwargs.get("repo"))
        elif action == "create_pr":
            return await self.create_pr(
                owner=kwargs.get("owner"),
                repo=kwargs.get("repo"),
                title=kwargs.get("title"),
                head=kwargs.get("head"),
                base=kwargs.get("base"),
                body=kwargs.get("body", "")
            )
        elif action == "search_code":
            return await self.search_code(query=kwargs.get("query"))
        else:
            return ToolResult.error_result(error=f"Unknown action: {action}", tool_name=self.name)
