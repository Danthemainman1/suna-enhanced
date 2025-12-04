"""
Workspace management for enterprise features.

Workspaces are the top-level organizational unit that contains teams,
agents, tasks, and other resources.
"""

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from core.services.supabase import DBConnection
from core.utils.logger import logger
from .models import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, Role
from .rbac import RBACManager
import re


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class WorkspaceManager:
    """Manager for workspace operations."""
    
    def __init__(self, db: Optional[DBConnection] = None):
        """Initialize workspace manager."""
        self.db = db or DBConnection()
        self.rbac_manager = RBACManager(db)
    
    async def create(
        self,
        name: str,
        owner_id: UUID,
        slug: Optional[str] = None,
        description: Optional[str] = None
    ) -> WorkspaceResponse:
        """
        Create a new workspace.
        
        The creator automatically becomes the OWNER.
        
        Args:
            name: Workspace name
            owner_id: ID of the user who will own the workspace
            slug: URL slug (auto-generated if not provided)
            description: Workspace description
            
        Returns:
            Created workspace
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            workspace_id = uuid4()
            
            # Generate slug if not provided
            if not slug:
                slug = slugify(name)
            
            # Ensure slug is unique
            slug = await self._ensure_unique_slug(slug)
            
            data = {
                "id": str(workspace_id),
                "name": name,
                "slug": slug,
                "description": description,
                "owner_id": str(owner_id),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            result = await client.table("workspaces").insert(data).execute()
            
            # Assign OWNER role to creator
            await self.rbac_manager.assign_role(
                owner_id,
                workspace_id,
                Role.OWNER
            )
            
            logger.info(
                f"Workspace created: id={workspace_id}, name={name}, owner={owner_id}"
            )
            
            return WorkspaceResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            raise
    
    async def get(self, workspace_id: UUID) -> Optional[WorkspaceResponse]:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace or None if not found
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspaces")\
                .select("*")\
                .eq("id", str(workspace_id))\
                .limit(1)\
                .execute()
            
            if result.data:
                return WorkspaceResponse(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting workspace: {e}")
            return None
    
    async def get_by_slug(self, slug: str) -> Optional[WorkspaceResponse]:
        """
        Get a workspace by slug.
        
        Args:
            slug: Workspace slug
            
        Returns:
            Workspace or None if not found
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            result = await client.table("workspaces")\
                .select("*")\
                .eq("slug", slug)\
                .limit(1)\
                .execute()
            
            if result.data:
                return WorkspaceResponse(**result.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting workspace by slug: {e}")
            return None
    
    async def update(
        self,
        workspace_id: UUID,
        updates: WorkspaceUpdate
    ) -> WorkspaceResponse:
        """
        Update a workspace.
        
        Args:
            workspace_id: Workspace ID
            updates: Fields to update
            
        Returns:
            Updated workspace
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            data = {
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if updates.name is not None:
                data["name"] = updates.name
            
            if updates.description is not None:
                data["description"] = updates.description
            
            result = await client.table("workspaces")\
                .update(data)\
                .eq("id", str(workspace_id))\
                .execute()
            
            logger.info(f"Workspace updated: id={workspace_id}")
            
            return WorkspaceResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error updating workspace: {e}")
            raise
    
    async def delete(
        self,
        workspace_id: UUID,
        confirmation: str
    ) -> bool:
        """
        Delete a workspace.
        
        Requires confirmation by passing the workspace name.
        
        Args:
            workspace_id: Workspace ID
            confirmation: Must match workspace name
            
        Returns:
            True if successful
        """
        try:
            # Get workspace to verify name
            workspace = await self.get(workspace_id)
            if not workspace:
                raise ValueError("Workspace not found")
            
            # Verify confirmation
            if workspace.name != confirmation:
                raise ValueError("Confirmation name does not match workspace name")
            
            await self.db.initialize()
            client = await self.db.client
            
            # Delete workspace (cascade will handle related records)
            await client.table("workspaces")\
                .delete()\
                .eq("id", str(workspace_id))\
                .execute()
            
            logger.info(f"Workspace deleted: id={workspace_id}, name={workspace.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting workspace: {e}")
            raise
    
    async def list_user_workspaces(
        self,
        user_id: UUID
    ) -> List[WorkspaceResponse]:
        """
        List all workspaces a user is a member of.
        
        Args:
            user_id: User ID
            
        Returns:
            List of workspaces
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            # Get workspace IDs from membership
            members_result = await client.table("workspace_members")\
                .select("workspace_id")\
                .eq("user_id", str(user_id))\
                .execute()
            
            workspace_ids = [row["workspace_id"] for row in members_result.data]
            
            if not workspace_ids:
                return []
            
            # Get workspace details
            workspaces_result = await client.table("workspaces")\
                .select("*")\
                .in_("id", workspace_ids)\
                .execute()
            
            return [WorkspaceResponse(**row) for row in workspaces_result.data]
            
        except Exception as e:
            logger.error(f"Error listing user workspaces: {e}")
            raise
    
    async def _ensure_unique_slug(self, slug: str) -> str:
        """
        Ensure slug is unique by appending a number if necessary.
        
        Args:
            slug: Desired slug
            
        Returns:
            Unique slug
        """
        try:
            await self.db.initialize()
            client = await self.db.client
            
            original_slug = slug
            counter = 1
            
            while True:
                result = await client.table("workspaces")\
                    .select("id")\
                    .eq("slug", slug)\
                    .limit(1)\
                    .execute()
                
                if not result.data:
                    return slug
                
                slug = f"{original_slug}-{counter}"
                counter += 1
                
        except Exception as e:
            logger.error(f"Error ensuring unique slug: {e}")
            raise
