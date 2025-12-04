# Enterprise Features Module

This module provides enterprise-grade features for Suna, including role-based access control, fine-grained permissions, audit logging, and more.

## Features

### 1. Role-Based Access Control (RBAC)
- **Module**: `rbac.py`
- **Hierarchy**: OWNER > ADMIN > MANAGER > MEMBER > VIEWER
- **Features**:
  - Assign roles to users in workspaces
  - Check role levels
  - Transfer ownership
  - List workspace members

### 2. Fine-Grained Permissions
- **Module**: `permissions.py`
- **Format**: `resource:action` (e.g., `agents:create`, `tasks:read`)
- **Features**:
  - Role-based permission mapping
  - Wildcard permissions (e.g., `agents:*`)
  - FastAPI dependency decorators for easy endpoint protection
  - Permission checking at runtime

### 3. Audit Logging
- **Module**: `audit_log.py`
- **Features**:
  - Log all significant events (who, what, when, where)
  - Track before/after state for changes
  - Query logs with filters and pagination
  - Export logs to JSON or CSV

### 4. Workspaces
- **Module**: `workspaces.py`
- **Features**:
  - Create and manage workspaces
  - Auto-generate URL slugs
  - Workspace ownership
  - List user workspaces

### 5. Teams
- **Module**: `teams.py`
- **Features**:
  - List team members
  - Update member roles
  - Remove members
  - Role hierarchy enforcement

### 6. Invitations
- **Module**: `invitations.py`
- **Features**:
  - Invite users to workspaces via email
  - Time-limited invitation tokens
  - Accept/revoke invitations
  - List pending invitations

### 7. API Keys
- **Module**: `api_keys.py`
- **Features**:
  - Generate secure API keys
  - Key hashing for storage
  - Scope-based permissions
  - Optional expiration
  - Redis-based rate limiting
  - Last used tracking

### 8. Usage Tracking
- **Module**: `usage_tracking.py`
- **Features**:
  - Track API calls
  - Track LLM token usage (input/output)
  - Get usage statistics by date range
  - Current month and daily usage reports

## API Endpoints

All endpoints are prefixed with `/api/enterprise`:

### Workspaces
- `POST /workspaces` - Create workspace
- `GET /workspaces` - List user workspaces
- `GET /workspaces/{id}` - Get workspace details
- `PATCH /workspaces/{id}` - Update workspace (requires ADMIN)
- `DELETE /workspaces/{id}` - Delete workspace (requires OWNER)

### Teams
- `GET /workspaces/{id}/members` - List team members
- `PATCH /workspaces/{id}/members/{user_id}/role` - Update role (requires ADMIN)
- `DELETE /workspaces/{id}/members/{user_id}` - Remove member (requires ADMIN)

### Invitations
- `POST /workspaces/{id}/invitations` - Create invitation (requires ADMIN)
- `GET /workspaces/{id}/invitations` - List pending invitations (requires ADMIN)
- `POST /invitations/{token}/accept` - Accept invitation
- `DELETE /workspaces/{id}/invitations/{id}` - Revoke invitation (requires ADMIN)

### API Keys
- `POST /workspaces/{id}/api-keys` - Create API key (requires MANAGER)
- `GET /workspaces/{id}/api-keys` - List API keys (requires MANAGER)
- `DELETE /workspaces/{id}/api-keys/{id}` - Revoke API key (requires MANAGER)

### Audit Logs
- `GET /workspaces/{id}/audit-logs` - Query audit logs (requires ADMIN)
- `GET /workspaces/{id}/audit-logs/export` - Export logs (requires ADMIN)

### Usage Stats
- `GET /workspaces/{id}/usage/current` - Current month usage (requires MEMBER)
- `GET /workspaces/{id}/usage` - Usage for date range (requires MEMBER)

## Database Schema

The module requires the following tables (see migration file):
- `workspaces` - Workspace metadata
- `workspace_members` - User-workspace-role mappings
- `workspace_invitations` - Pending invitations
- `api_keys` - API key metadata
- `audit_logs` - Audit event logs
- `usage_metrics` - Usage tracking data

## Role Permissions

### OWNER
- All permissions including:
  - Delete workspace
  - Transfer ownership

### ADMIN
- Manage users, agents, settings
- View billing and audit logs
- Cannot delete workspace or transfer ownership

### MANAGER
- Create/edit agents
- Run tasks and workflows
- Manage API keys
- Cannot manage team or billing

### MEMBER
- Run tasks and workflows
- View agents and results
- Cannot create/edit agents

### VIEWER
- Read-only access
- View agents, tasks, workflows, settings

## Usage Examples

### Python

```python
from enterprise import (
    RBACManager,
    WorkspaceManager,
    PermissionChecker,
    Role
)

# Create a workspace
workspace_manager = WorkspaceManager()
workspace = await workspace_manager.create(
    name="My Company",
    owner_id=user_id
)

# Assign a role
rbac_manager = RBACManager()
await rbac_manager.assign_role(
    user_id=team_member_id,
    workspace_id=workspace.id,
    role=Role.ADMIN
)

# Check permissions
checker = PermissionChecker()
has_perm = await checker.has_permission(
    user_id=team_member_id,
    workspace_id=workspace.id,
    permission="agents:create"
)
```

### FastAPI

```python
from fastapi import APIRouter, Depends
from enterprise.permissions import require_permission, require_role
from enterprise.models import Role

router = APIRouter()

@router.post("/agents")
async def create_agent(
    workspace_id: UUID,
    _: None = Depends(require_permission("agents:create"))
):
    # Create agent logic
    pass

@router.delete("/workspace/{workspace_id}")
async def delete_workspace(
    workspace_id: UUID,
    _: None = Depends(require_role(Role.OWNER))
):
    # Delete workspace logic
    pass
```

## Testing

Run tests with:
```bash
pytest tests/test_enterprise/ -v
```

All tests use mocked database connections and are safe to run without a real database.

## Security Considerations

1. **API Keys**: Stored as SHA-256 hashes, never plain text
2. **Invitations**: Time-limited tokens with secure generation
3. **Audit Logs**: Immutable, track all significant events
4. **Rate Limiting**: Redis-based sliding window for API keys
5. **Row Level Security**: Database policies enforce workspace isolation
6. **Permission Checks**: All sensitive endpoints protected by RBAC/permissions

## Dependencies

- FastAPI
- Supabase (PostgreSQL)
- Redis (for rate limiting)
- Pydantic v2
- Python 3.11+
