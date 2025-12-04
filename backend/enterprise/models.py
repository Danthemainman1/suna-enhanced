"""
Pydantic models for enterprise features.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


# Enums
class Role(str, Enum):
    """User roles in workspace hierarchy."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class AuditEventType(str, Enum):
    """Types of audit events."""
    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    
    # Agents
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"
    AGENT_DELETED = "agent.deleted"
    AGENT_EXECUTED = "agent.executed"
    
    # Tasks
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    
    # Team
    TEAM_MEMBER_ADDED = "team.member_added"
    TEAM_MEMBER_REMOVED = "team.member_removed"
    TEAM_MEMBER_ROLE_UPDATED = "team.member_role_updated"
    
    # API Keys
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    
    # Workspaces
    WORKSPACE_CREATED = "workspace.created"
    WORKSPACE_UPDATED = "workspace.updated"
    WORKSPACE_DELETED = "workspace.deleted"
    
    # Settings
    SETTINGS_UPDATED = "settings.updated"


# Workspace Models
class WorkspaceCreate(BaseModel):
    """Request to create a workspace."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    """Request to update a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    """Workspace response model."""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


# Team Models
class TeamMemberResponse(BaseModel):
    """Team member response model."""
    user_id: UUID
    workspace_id: UUID
    role: Role
    email: str
    name: Optional[str] = None
    joined_at: datetime


class UpdateRoleRequest(BaseModel):
    """Request to update a team member's role."""
    role: Role


# Invitation Models
class InvitationCreate(BaseModel):
    """Request to create an invitation."""
    email: EmailStr
    role: Role


class InvitationResponse(BaseModel):
    """Invitation response model."""
    id: UUID
    workspace_id: UUID
    email: EmailStr
    role: Role
    invited_by: UUID
    token: str
    expires_at: datetime
    created_at: datetime


# API Key Models
class APIKeyCreate(BaseModel):
    """Request to create an API key."""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response model (masked)."""
    id: UUID
    workspace_id: UUID
    name: str
    key_preview: str  # First 8 chars + ...
    scopes: List[str]
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime


class APIKeyCreateResponse(BaseModel):
    """Response when creating an API key (includes plain key)."""
    id: UUID
    workspace_id: UUID
    name: str
    key: str  # Full plain key - only shown once
    scopes: List[str]
    expires_at: Optional[datetime] = None
    created_at: datetime


# Audit Log Models
class AuditLogEntry(BaseModel):
    """Audit log entry model."""
    id: UUID
    workspace_id: UUID
    user_id: Optional[UUID] = None
    event_type: AuditEventType
    resource_type: str
    resource_id: Optional[str] = None
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AuditLogQuery(BaseModel):
    """Query parameters for audit logs."""
    event_type: Optional[AuditEventType] = None
    resource_type: Optional[str] = None
    user_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=100)


class AuditLogListResponse(BaseModel):
    """Response for audit log list."""
    entries: List[AuditLogEntry]
    total: int
    page: int
    per_page: int
    pages: int


# Usage Tracking Models
class UsageStats(BaseModel):
    """Usage statistics model."""
    workspace_id: UUID
    api_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    period_start: datetime
    period_end: datetime


# RBAC Models
class RoleAssignment(BaseModel):
    """Role assignment model."""
    user_id: UUID
    workspace_id: UUID
    role: Role
    assigned_at: datetime
    assigned_by: Optional[UUID] = None


class TransferOwnershipRequest(BaseModel):
    """Request to transfer workspace ownership."""
    new_owner_id: UUID
    confirmation: str = Field(..., description="Must be the workspace name")
