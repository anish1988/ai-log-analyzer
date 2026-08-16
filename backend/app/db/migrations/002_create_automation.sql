-- =============================================================================
-- PHASE 3 - AUTOMATION PERSISTENCE
-- =============================================================================
--
-- Purpose:
--   Persistent state for standalone automated log analysis.
--
-- Tables:
--   1. automation_runs
--   2. automation_run_servers
--   3. automation_checkpoints
--   4. automation_audit_events
--
-- Important:
--   Run history and checkpoint state are intentionally separate.
--
-- =============================================================================


-- =============================================================================
-- 1. AUTOMATION RUNS
-- =============================================================================

CREATE TABLE IF NOT EXISTS automation_runs (

    id BIGSERIAL PRIMARY KEY,

    run_id VARCHAR(100) NOT NULL UNIQUE,

    status VARCHAR(30) NOT NULL DEFAULT 'running',

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    completed_at TIMESTAMPTZ,

    servers_total INTEGER NOT NULL DEFAULT 0,

    servers_processed INTEGER NOT NULL DEFAULT 0,

    logs_total INTEGER NOT NULL DEFAULT 0,

    logs_processed INTEGER NOT NULL DEFAULT 0,

    lines_read BIGINT NOT NULL DEFAULT 0,

    errors_detected INTEGER NOT NULL DEFAULT 0,

    analyses_completed INTEGER NOT NULL DEFAULT 0,

    jira_tickets_created INTEGER NOT NULL DEFAULT 0,

    jira_tickets_failed INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);


CREATE INDEX IF NOT EXISTS idx_automation_runs_status
ON automation_runs (status);


CREATE INDEX IF NOT EXISTS idx_automation_runs_started_at
ON automation_runs (started_at DESC);


-- =============================================================================
-- 2. AUTOMATION RUN SERVERS
-- =============================================================================
--
-- One row represents one configured server during one automation run.
--

CREATE TABLE IF NOT EXISTS automation_run_servers (

    id BIGSERIAL PRIMARY KEY,

    run_id VARCHAR(100) NOT NULL,

    server_id VARCHAR(100) NOT NULL,

    server_ip VARCHAR(255),

    server_type VARCHAR(50),

    status VARCHAR(30) NOT NULL DEFAULT 'pending',

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    logs_total INTEGER NOT NULL DEFAULT 0,

    logs_processed INTEGER NOT NULL DEFAULT 0,

    lines_read BIGINT NOT NULL DEFAULT 0,

    errors_detected INTEGER NOT NULL DEFAULT 0,

    analyses_completed INTEGER NOT NULL DEFAULT 0,

    jira_tickets_created INTEGER NOT NULL DEFAULT 0,

    jira_tickets_failed INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_automation_run_servers_run
        FOREIGN KEY (run_id)
        REFERENCES automation_runs (run_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_automation_run_server
        UNIQUE (run_id, server_id)

);


CREATE INDEX IF NOT EXISTS idx_automation_run_servers_run_id
ON automation_run_servers (run_id);


CREATE INDEX IF NOT EXISTS idx_automation_run_servers_server_id
ON automation_run_servers (server_id);


-- =============================================================================
-- 3. AUTOMATION CHECKPOINTS
-- =============================================================================
--
-- One checkpoint represents the current read position of one log source.
--
-- Identity:
--
--     server_id
--     log_type
--     file_path
--
-- This table is NOT tied to a particular run.
--
-- It represents the persistent state used by the NEXT run.
--
-- =============================================================================

CREATE TABLE IF NOT EXISTS automation_checkpoints (

    id BIGSERIAL PRIMARY KEY,

    server_id VARCHAR(100) NOT NULL,

    server_ip VARCHAR(255),

    log_type VARCHAR(100) NOT NULL,

    file_path TEXT NOT NULL,

    last_offset BIGINT NOT NULL DEFAULT 0,

    last_line_number BIGINT NOT NULL DEFAULT 0,

    file_size BIGINT NOT NULL DEFAULT 0,

    file_inode BIGINT,

    last_read_at TIMESTAMPTZ,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_automation_checkpoint
        UNIQUE (
            server_id,
            log_type,
            file_path
        )

);


CREATE INDEX IF NOT EXISTS idx_automation_checkpoints_server
ON automation_checkpoints (server_id);


CREATE INDEX IF NOT EXISTS idx_automation_checkpoints_log_type
ON automation_checkpoints (log_type);


-- =============================================================================
-- 4. AUTOMATION AUDIT EVENTS
-- =============================================================================
--
-- Stores request/response information for every important automation step.
--
-- Examples:
--
--     run_started
--     server_started
--     log_fetch_started
--     log_fetch_completed
--     parser_completed
--     rag_completed
--     llm_completed
--     jira_completed
--     checkpoint_updated
--     run_completed
--
-- =============================================================================

CREATE TABLE IF NOT EXISTS automation_audit_events (

    id BIGSERIAL PRIMARY KEY,

    run_id VARCHAR(100) NOT NULL,

    server_id VARCHAR(100),

    log_type VARCHAR(100),

    step VARCHAR(100) NOT NULL,

    status VARCHAR(30) NOT NULL,

    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    message TEXT NOT NULL DEFAULT '',

    request JSONB NOT NULL DEFAULT '{}'::jsonb,

    response JSONB NOT NULL DEFAULT '{}'::jsonb,

    error TEXT,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_automation_audit_run
        FOREIGN KEY (run_id)
        REFERENCES automation_runs (run_id)
        ON DELETE CASCADE

);


CREATE INDEX IF NOT EXISTS idx_automation_audit_run_id
ON automation_audit_events (run_id);


CREATE INDEX IF NOT EXISTS idx_automation_audit_timestamp
ON automation_audit_events (timestamp DESC);


CREATE INDEX IF NOT EXISTS idx_automation_audit_step
ON automation_audit_events (step);