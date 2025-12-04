# Enterprise Features Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│                         /api/enterprise/*                        │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Enterprise Router (api.py)                  │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │Workspaces│  Teams   │Invites   │ API Keys │ Audit/Usage  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
└───────┬──────────────────────────────────────────────┬──────────┘
        │                                              │
        ▼                                              ▼
┌──────────────────────────────────┐    ┌────────────────────────┐
│   Permission & RBAC Layers       │    │   Audit & Usage        │
│                                  │    │   Tracking             │
│  ┌─────────────────────────┐    │    │                        │
│  │ PermissionChecker       │    │    │  ┌──────────────────┐  │
│  │  - has_permission()     │    │    │  │ AuditLog         │  │
│  │  - check_permission()   │    │    │  │  - log()         │  │
│  └──────────┬──────────────┘    │    │  │  - query()       │  │
│             │                    │    │  │  - export()      │  │
│             ▼                    │    │  └──────────────────┘  │
│  ┌─────────────────────────┐    │    │  ┌──────────────────┐  │
│  │ RBACManager             │    │    │  │ UsageTracker     │  │
│  │  - assign_role()        │    │    │  │  - record_*()    │  │
│  │  - get_role()           │    │    │  │  - get_usage()   │  │
│  │  - check_role_level()   │    │    │  └──────────────────┘  │
│  └─────────────────────────┘    │    │                        │
└───────────────┬──────────────────┘    └────────────┬───────────┘
                │                                    │
                ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Core Managers Layer                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Workspace    │  │ Team         │  │ Invitation   │         │
│  │ Manager      │  │ Manager      │  │ Manager      │         │
│  │              │  │              │  │              │         │
│  │ - create()   │  │ - list()     │  │ - create()   │         │
│  │ - update()   │  │ - update()   │  │ - accept()   │         │
│  │ - delete()   │  │ - remove()   │  │ - revoke()   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐                                               │
│  │ APIKey       │                                               │
│  │ Manager      │                                               │
│  │              │                                               │
│  │ - create()   │──────────┐                                   │
│  │ - validate() │          │                                   │
│  │ - revoke()   │          │                                   │
│  │ - rate_limit()│         │                                   │
│  └──────────────┘          │                                   │
└────────────────────────────┼───────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Redis          │
                    │ (Rate Limiting)│
                    └────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supabase PostgreSQL                          │
│                                                                  │
│  Tables:                           Security:                    │
│  ┌────────────────────────┐        ┌─────────────────────┐     │
│  │ workspaces             │        │ Row Level Security  │     │
│  │ workspace_members      │        │ (RLS) Policies      │     │
│  │ workspace_invitations  │        │                     │     │
│  │ api_keys               │        │ - Workspace         │     │
│  │ audit_logs             │        │   isolation         │     │
│  │ usage_metrics          │        │ - Role-based access │     │
│  └────────────────────────┘        └─────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### 1. Create Workspace with Owner

```
User Request
    │
    ▼
POST /api/enterprise/workspaces
    │
    ▼
[Authentication Layer]
    │
    ▼
WorkspaceManager.create()
    │
    ├──▶ Generate slug
    │
    ├──▶ Insert into 'workspaces' table
    │
    └──▶ RBACManager.assign_role(OWNER)
        │
        └──▶ Insert into 'workspace_members'
    │
    ▼
AuditLog.log(WORKSPACE_CREATED)
    │
    └──▶ Insert into 'audit_logs'
    │
    ▼
Return WorkspaceResponse
```

### 2. Protected Endpoint Access

```
User Request
    │
    ▼
POST /api/enterprise/workspaces/{id}/api-keys
    │
    ▼
[Authentication] → verify JWT
    │
    ▼
[Permission Dependency] → require_role(MANAGER)
    │
    ├──▶ RBACManager.get_role()
    │
    ├──▶ Check role >= MANAGER
    │
    └──▶ [Pass/Fail] → 200 or 403
    │
    ▼
APIKeyManager.create()
    │
    ├──▶ Generate secure key
    │
    ├──▶ Hash with SHA-256
    │
    └──▶ Insert into 'api_keys'
    │
    ▼
AuditLog.log(API_KEY_CREATED)
    │
    ▼
Return APIKeyCreateResponse (with plain key - only time!)
```

### 3. API Key Rate Limiting

```
API Request with Key
    │
    ▼
APIKeyManager.validate(key)
    │
    ├──▶ Hash key
    │
    ├──▶ Query 'api_keys' table
    │
    ├──▶ Check expiration
    │
    └──▶ [Valid/Invalid]
    │
    ▼
APIKeyManager.check_rate_limit()
    │
    ├──▶ Redis: ZREMRANGEBYSCORE (clean old)
    │
    ├──▶ Redis: ZADD (add current request)
    │
    ├──▶ Redis: ZCARD (count requests)
    │
    └──▶ [Allow/Deny] → 200 or 429
    │
    ▼
UsageTracker.record_api_call()
    │
    └──▶ Insert into 'usage_metrics'
```

## Role Hierarchy & Permissions

```
┌─────────────────────────────────────────────────────────────┐
│                         OWNER                               │
│  • Full access to everything                                │
│  • Delete workspace                                         │
│  • Transfer ownership                                       │
│  • All ADMIN permissions                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         ADMIN                               │
│  • Manage users (invite, remove, update roles)              │
│  • Manage agents (create, update, delete)                   │
│  • Manage settings                                          │
│  • View billing and audit logs                              │
│  • All MANAGER permissions                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        MANAGER                              │
│  • Create/edit agents                                       │
│  • Run tasks and workflows                                  │
│  • Manage API keys                                          │
│  • All MEMBER permissions                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         MEMBER                              │
│  • Run tasks and workflows                                  │
│  • View results                                             │
│  • All VIEWER permissions                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         VIEWER                              │
│  • Read-only access                                         │
│  • View agents, tasks, workflows                            │
│  • View settings                                            │
└─────────────────────────────────────────────────────────────┘
```

## Permission Format

```
resource:action

Examples:
  agents:create      - Create agents
  agents:read        - View agents
  agents:update      - Edit agents
  agents:delete      - Delete agents
  agents:execute     - Run agents
  agents:*           - All agent permissions (wildcard)
  
  tasks:create       - Create tasks
  tasks:read         - View tasks
  tasks:cancel       - Cancel tasks
  
  team:invite        - Invite team members
  team:remove        - Remove team members
  team:update_roles  - Update member roles
  
  billing:read       - View billing info
  billing:update     - Update billing settings
  
  audit:read         - View audit logs
  
  api_keys:create    - Create API keys
  api_keys:revoke    - Revoke API keys
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Authentication Layer                                     │
│    - JWT token verification                                 │
│    - User identity validation                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Authorization Layer (RBAC + Permissions)                 │
│    - Role checking (require_role decorator)                 │
│    - Permission checking (require_permission decorator)     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Database Layer (Row Level Security)                      │
│    - PostgreSQL RLS policies                                │
│    - Workspace isolation                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Audit Layer                                              │
│    - All significant actions logged                         │
│    - Immutable audit trail                                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Async/Await Throughout
All operations are async to support high concurrency and non-blocking I/O.

### 2. Dependency Injection
FastAPI dependencies used for clean, testable permission checking.

### 3. Database-First Security
Row Level Security (RLS) in PostgreSQL provides defense-in-depth.

### 4. Fail-Safe Design
Usage tracking failures don't break requests - graceful degradation.

### 5. Token-Based Invitations
Stateless, time-limited tokens for secure workspace invitations.

### 6. Hashed API Keys
Keys never stored in plain text - SHA-256 hashing for security.

### 7. Redis Rate Limiting
Sliding window algorithm for accurate, distributed rate limiting.

### 8. Complete Audit Trail
Every significant action logged with context for compliance.

## Extension Points

### Adding New Roles
1. Add to `Role` enum in `models.py`
2. Add to `ROLE_HIERARCHY` in `rbac.py`
3. Define permissions in `ROLE_PERMISSIONS` in `permissions.py`
4. Update database enum type in migration

### Adding New Permissions
1. Add to role permission sets in `permissions.py`
2. Use in endpoint decorators
3. Document in README

### Adding New Audit Events
1. Add to `AuditEventType` enum in `models.py`
2. Call `audit_log.log()` in relevant code
3. Update event documentation

### Adding New Metrics
1. Add tracking call in relevant code
2. Use `UsageTracker.record_*()` methods
3. Query with existing methods

## Performance Considerations

1. **Database Indexes**: All foreign keys and frequently queried columns indexed
2. **Connection Pooling**: Supabase client uses connection pooling
3. **Async I/O**: Non-blocking database and Redis operations
4. **Rate Limiting**: Redis-based for low latency
5. **Query Optimization**: Selective field loading, pagination support
6. **Caching Opportunity**: Role/permission checks could be cached

## Testing Strategy

1. **Unit Tests**: Mock database, test business logic
2. **Integration Tests**: Real database, test end-to-end flows
3. **Markers**: `@pytest.mark.integration` for database tests
4. **Fixtures**: Reusable mocks in `conftest.py`
5. **Coverage**: 81 tests covering all major code paths
