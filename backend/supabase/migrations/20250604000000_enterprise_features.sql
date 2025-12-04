-- Enterprise Features Schema
-- Phase 4: RBAC, permissions, audit logging, workspaces, teams, and API keys

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create role enum type
DO $$ BEGIN
    CREATE TYPE enterprise_role AS ENUM ('owner', 'admin', 'manager', 'member', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Workspace members (RBAC)
CREATE TABLE IF NOT EXISTS workspace_members (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    role enterprise_role NOT NULL DEFAULT 'member',
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    PRIMARY KEY (user_id, workspace_id)
);

-- Workspace invitations
CREATE TABLE IF NOT EXISTS workspace_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role enterprise_role NOT NULL DEFAULT 'member',
    invited_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    key_preview TEXT NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT '{}',
    created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    action TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Usage metrics
CREATE TABLE IF NOT EXISTS usage_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    endpoint TEXT,
    method TEXT,
    model TEXT,
    provider TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_workspace_members_user ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_workspace ON workspace_invitations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_token ON workspace_invitations(token);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_email ON workspace_invitations(email);
CREATE INDEX IF NOT EXISTS idx_api_keys_workspace ON api_keys(workspace_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace ON audit_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_workspace ON usage_metrics(workspace_id);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_timestamp ON usage_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_type ON usage_metrics(metric_type);

-- Update trigger for workspaces
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_workspaces_updated_at ON workspaces;
CREATE TRIGGER update_workspaces_updated_at
    BEFORE UPDATE ON workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_metrics ENABLE ROW LEVEL SECURITY;

-- Workspaces: Users can see workspaces they're members of
CREATE POLICY workspaces_select_policy ON workspaces
    FOR SELECT USING (
        id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY workspaces_insert_policy ON workspaces
    FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY workspaces_update_policy ON workspaces
    FOR UPDATE USING (
        id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY workspaces_delete_policy ON workspaces
    FOR DELETE USING (
        id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role = 'owner'
        )
    );

-- Workspace members: Users can see members of their workspaces
CREATE POLICY workspace_members_select_policy ON workspace_members
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY workspace_members_insert_policy ON workspace_members
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY workspace_members_delete_policy ON workspace_members
    FOR DELETE USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- Invitations: Admins can manage invitations
CREATE POLICY invitations_select_policy ON workspace_invitations
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY invitations_insert_policy ON workspace_invitations
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY invitations_delete_policy ON workspace_invitations
    FOR DELETE USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

-- API keys: Managers can manage API keys
CREATE POLICY api_keys_select_policy ON api_keys
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'manager')
        )
    );

CREATE POLICY api_keys_insert_policy ON api_keys
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'manager')
        )
    );

CREATE POLICY api_keys_delete_policy ON api_keys
    FOR DELETE USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin', 'manager')
        )
    );

-- Audit logs: Admins can read audit logs
CREATE POLICY audit_logs_select_policy ON audit_logs
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
            AND role IN ('owner', 'admin')
        )
    );

CREATE POLICY audit_logs_insert_policy ON audit_logs
    FOR INSERT WITH CHECK (true); -- Allow all inserts (system-generated)

-- Usage metrics: Members can read usage metrics
CREATE POLICY usage_metrics_select_policy ON usage_metrics
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY usage_metrics_insert_policy ON usage_metrics
    FOR INSERT WITH CHECK (true); -- Allow all inserts (system-generated)

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON workspaces TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_members TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON workspace_invitations TO authenticated, service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON api_keys TO authenticated, service_role;
GRANT SELECT, INSERT ON audit_logs TO authenticated, service_role;
GRANT SELECT, INSERT ON usage_metrics TO authenticated, service_role;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated, service_role;
