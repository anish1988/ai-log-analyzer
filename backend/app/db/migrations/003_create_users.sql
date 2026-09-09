-- =============================================================================
-- PHASE 4 - USER FOUNDATION
-- =============================================================================
--
-- Purpose:
--   Create the application user foundation for Phase 4.
--
-- Important:
--   This migration is intentionally independent from automation tables.
--
--   Automation tables:
--       automation_runs
--       automation_run_servers
--       automation_checkpoints
--       automation_audit_events
--
--   MUST NOT depend on users.
--
-- Authentication providers:
--   local
--   google
--   sso
--
-- Authentication itself will be implemented later in Phase 4.13.
--
-- =============================================================================


-- =============================================================================
-- 1. USERS
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email VARCHAR(320) NOT NULL,

    display_name VARCHAR(255),

    role VARCHAR(30) NOT NULL DEFAULT 'user',

    auth_provider VARCHAR(30) NOT NULL DEFAULT 'local',

    provider_subject VARCHAR(255),

    password_hash TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    last_login_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_users_email
        UNIQUE (email),

    CONSTRAINT uq_users_provider_subject
        UNIQUE (auth_provider, provider_subject),

    CONSTRAINT chk_users_role
        CHECK (
            role IN (
                'user',
                'admin',
                'superadmin'
            )
        ),

    CONSTRAINT chk_users_auth_provider
        CHECK (
            auth_provider IN (
                'local',
                'google',
                'sso'
            )
        )

);


-- =============================================================================
-- 2. INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_users_email
ON users (email);

CREATE INDEX IF NOT EXISTS idx_users_role
ON users (role);

CREATE INDEX IF NOT EXISTS idx_users_active
ON users (is_active);

CREATE INDEX IF NOT EXISTS idx_users_provider
ON users (auth_provider);


-- =============================================================================
-- 3. DEVELOPMENT DEFAULT USERS
-- =============================================================================
--
-- These users are only development/bootstrap identities.
--
-- They do NOT provide authentication.
--
-- Authentication credentials will be introduced in Phase 4.13.
--
-- =============================================================================

INSERT INTO users (
    email,
    display_name,
    role,
    auth_provider,
    provider_subject,
    password_hash,
    is_active
)
VALUES (
    'dev-user@local',
    'Development User',
    'user',
    'local',
    NULL,
    NULL,
    TRUE
)
ON CONFLICT (email) DO NOTHING;


INSERT INTO users (
    email,
    display_name,
    role,
    auth_provider,
    provider_subject,
    password_hash,
    is_active
)
VALUES (
    'admin@local',
    'Development Admin',
    'admin',
    'local',
    NULL,
    NULL,
    TRUE
)
ON CONFLICT (email) DO NOTHING;


INSERT INTO users (
    email,
    display_name,
    role,
    auth_provider,
    provider_subject,
    password_hash,
    is_active
)
VALUES (
    'superadmin@local',
    'Development SuperAdmin',
    'superadmin',
    'local',
    NULL,
    NULL,
    TRUE
)
ON CONFLICT (email) DO NOTHING;