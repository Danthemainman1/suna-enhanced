"""
Fine-grained permissions system for enterprise features.

Permission format: resource:action
Examples: agents:create, tasks:read, settings:update
"""

from typing import List, Optional, Set
from uuid import UUID
from fastapi import Depends, HTTPException, status
from core.utils.auth_utils import verify_and_get_user_id_from_jwt
from core.utils.logger import logger
from .rbac import RBACManager, Role
from .models import Role as RoleEnum


# Permission definitions by role
ROLE_PERMISSIONS = {
    Role.OWNER: {
        # All permissions
        "agents:*",
        "tasks:*",
        "workflows:*",
        "tools:*",
        "settings:*",
        "team:*",
        "billing:*",
        "audit:*",
        "api_keys:*",
        "workspace:delete",
        "workspace:transfer",
    },
    Role.ADMIN: {
        "agents:*",
        "tasks:*",
        "workflows:*",
        "tools:*",
        "settings:*",
        "team:view",
        "team:invite",
        "team:remove",
        "team:update_roles",
        "billing:read",
        "audit:read",
        "api_keys:*",
    },
    Role.MANAGER: {
        "agents:create",
        "agents:read",
        "agents:update",
        "agents:execute",
        "tasks:create",
        "tasks:read",
        "tasks:cancel",
        "workflows:create",
        "workflows:read",
        "workflows:update",
        "workflows:execute",
        "tools:use",
        "settings:read",
        "team:view",
        "api_keys:create",
        "api_keys:read",
    },
    Role.MEMBER: {
        "agents:read",
        "agents:execute",
        "tasks:create",
        "tasks:read",
        "workflows:read",
        "workflows:execute",
        "tools:use",
        "settings:read",
        "team:view",
    },
    Role.VIEWER: {
        "agents:read",
        "tasks:read",
        "workflows:read",
        "settings:read",
        "team:view",
    },
}


class PermissionChecker:
    """Check permissions for users in workspaces."""
    
    def __init__(self, rbac_manager: Optional[RBACManager] = None):
        """Initialize permission checker."""
        self.rbac_manager = rbac_manager or RBACManager()
    
    async def has_permission(
        self,
        user_id: UUID,
        workspace_id: UUID,
        permission: str
    ) -> bool:
        """
        Check if a user has a specific permission in a workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            permission: Permission to check (format: resource:action)
            
        Returns:
            True if user has the permission
        """
        try:
            # Get user's role
            role = await self.rbac_manager.get_role(user_id, workspace_id)
            if not role:
                return False
            
            # Get permissions for role
            permissions = await self.get_user_permissions(user_id, workspace_id)
            
            # Check exact match
            if permission in permissions:
                return True
            
            # Check wildcard permissions (e.g., agents:* for agents:create)
            resource = permission.split(":")[0] if ":" in permission else ""
            wildcard = f"{resource}:*"
            if wildcard in permissions:
                return True
            
            # Check global wildcard
            if "*:*" in permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def get_user_permissions(
        self,
        user_id: UUID,
        workspace_id: UUID
    ) -> Set[str]:
        """
        Get all permissions for a user in a workspace.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            
        Returns:
            Set of permissions
        """
        try:
            role = await self.rbac_manager.get_role(user_id, workspace_id)
            if not role:
                return set()
            
            return ROLE_PERMISSIONS.get(role, set()).copy()
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return set()
    
    async def check_permission(
        self,
        user_id: UUID,
        workspace_id: UUID,
        permission: str
    ) -> None:
        """
        Check permission and raise HTTPException if not authorized.
        
        Args:
            user_id: User ID
            workspace_id: Workspace ID
            permission: Permission to check
            
        Raises:
            HTTPException: If user doesn't have permission
        """
        has_perm = await self.has_permission(user_id, workspace_id, permission)
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )


def require_permission(permission: str):
    """
    FastAPI dependency decorator to require a specific permission.
    
    Usage:
        @router.post("/agents")
        async def create_agent(
            workspace_id: UUID,
            user_id: str = Depends(verify_and_get_user_id_from_jwt),
            _: None = Depends(require_permission("agents:create"))
        ):
            ...
    
    Args:
        permission: Permission required (format: resource:action)
        
    Returns:
        FastAPI dependency function
    """
    async def dependency(
        workspace_id: UUID,
        user_id: str = Depends(verify_and_get_user_id_from_jwt)
    ) -> None:
        """Check if user has required permission."""
        checker = PermissionChecker()
        await checker.check_permission(
            UUID(user_id),
            workspace_id,
            permission
        )
    
    return dependency


def require_role(minimum_role: RoleEnum):
    """
    FastAPI dependency decorator to require a minimum role level.
    
    Usage:
        @router.delete("/workspace/{workspace_id}")
        async def delete_workspace(
            workspace_id: UUID,
            user_id: str = Depends(verify_and_get_user_id_from_jwt),
            _: None = Depends(require_role(Role.OWNER))
        ):
            ...
    
    Args:
        minimum_role: Minimum role required
        
    Returns:
        FastAPI dependency function
    """
    async def dependency(
        workspace_id: UUID,
        user_id: str = Depends(verify_and_get_user_id_from_jwt)
    ) -> None:
        """Check if user has required role level."""
        rbac_manager = RBACManager()
        has_role = await rbac_manager.check_role_level(
            UUID(user_id),
            workspace_id,
            minimum_role
        )
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum_role.value} role or higher"
            )
    
    return dependency
