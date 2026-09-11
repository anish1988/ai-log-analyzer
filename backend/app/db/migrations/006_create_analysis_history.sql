-- =============================================================================
-- ANALYSIS HISTORY & PERSISTENCE
-- =============================================================================
--
-- Purpose:
--   Persistent history for AI analysis executions and their individual
--   analysis results.
--
-- Tables:
--   1. analysis_runs
--   2. analysis_results
--
-- Design:
--   analysis_runs    = one complete AI analysis execution
--   analysis_results = one analyzed error belonging to an analysis run
--
-- Supports:
--   - Manual/browser analysis
--   - Automated analysis
--   - User-based history
--   - RAG/LLM result reporting
--   - Jira result tracking
--   - Complete raw request/response preservation
--
-- =============================================================================


-- =============================================================================
-- 1. ANALYSIS RUNS
-- =============================================================================
--
-- One row represents one complete AI analysis execution.
--
-- source_type:
--     manual
--     automation
--
-- automation_run_id:
--     References the existing automation run identifier logically.
--     It is intentionally not a foreign key because automation_runs uses
--     its own run lifecycle and identifier.
--
-- =============================================================================

CREATE TABLE IF NOT EXISTS analysis_runs (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    request_id VARCHAR(255),

    user_id UUID NOT NULL,

    source_type VARCHAR(30) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'processing',

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    completed_at TIMESTAMPTZ,

    total_errors INTEGER NOT NULL DEFAULT 0,

    completed_errors INTEGER NOT NULL DEFAULT 0,

    failed_errors INTEGER NOT NULL DEFAULT 0,

    log_type VARCHAR(100),

    servers JSONB NOT NULL DEFAULT '[]'::jsonb,

    log_files JSONB NOT NULL DEFAULT '[]'::jsonb,

    custom_prompt TEXT,

    automation_run_id VARCHAR(100),

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_analysis_runs_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_analysis_runs_source_type
        CHECK (
            source_type IN (
                'manual',
                'automation'
            )
        ),

    CONSTRAINT chk_analysis_runs_status
        CHECK (
            status IN (
                'processing',
                'completed',
                'failed',
                'error'
            )
        ),

    CONSTRAINT chk_analysis_runs_error_counts
        CHECK (
            total_errors >= 0
            AND completed_errors >= 0
            AND failed_errors >= 0
        )

);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_user_id
ON analysis_runs (user_id);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_user_created
ON analysis_runs (
    user_id,
    created_at DESC
);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_source_type
ON analysis_runs (source_type);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_status
ON analysis_runs (status);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_started_at
ON analysis_runs (started_at DESC);


CREATE INDEX IF NOT EXISTS idx_analysis_runs_automation_run_id
ON analysis_runs (automation_run_id);


-- =============================================================================
-- 2. ANALYSIS RESULTS
-- =============================================================================
--
-- One row represents one analyzed error.
--
-- Normalized columns are provided for filtering/reporting.
-- JSONB columns preserve the complete structured information.
--
-- =============================================================================

CREATE TABLE IF NOT EXISTS analysis_results (

    id BIGSERIAL PRIMARY KEY,

    analysis_run_id UUID NOT NULL,

    error_id VARCHAR(255) NOT NULL,

    error_signature VARCHAR(500),

    tier VARCHAR(100),

    log_type VARCHAR(100),

    server VARCHAR(255),

    file_name VARCHAR(500),

    file_path TEXT,

    title TEXT,

    severity VARCHAR(30),

    timestamp TIMESTAMPTZ,

    start_line INTEGER,

    end_line INTEGER,

    source VARCHAR(30),

    rag_match BOOLEAN NOT NULL DEFAULT FALSE,

    rag_knowledge_id BIGINT,

    rag_similarity DOUBLE PRECISION,

    confidence VARCHAR(50),

    analysis_status VARCHAR(50),

    error_summary TEXT,

    root_cause TEXT,

    solution TEXT,

    optimization TEXT,

    source_code_analysis TEXT,

    source_file TEXT,

    source_line_number INTEGER,

    jira_description TEXT,

    jira_issue_key VARCHAR(100),

    jira_issue_id VARCHAR(100),

    jira_issue_url TEXT,

    jira_status VARCHAR(50),

    root_cause_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,

    test_result JSONB NOT NULL DEFAULT '{}'::jsonb,

    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,

    source_code_location JSONB NOT NULL DEFAULT '{}'::jsonb,

    missing_information JSONB NOT NULL DEFAULT '[]'::jsonb,

    request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    response_payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    jira_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_analysis_results_run
        FOREIGN KEY (analysis_run_id)
        REFERENCES analysis_runs (id)
        ON DELETE CASCADE

);


CREATE INDEX IF NOT EXISTS idx_analysis_results_run_id
ON analysis_results (analysis_run_id);


CREATE INDEX IF NOT EXISTS idx_analysis_results_error_id
ON analysis_results (error_id);


CREATE INDEX IF NOT EXISTS idx_analysis_results_error_signature
ON analysis_results (error_signature);


CREATE INDEX IF NOT EXISTS idx_analysis_results_log_type
ON analysis_results (log_type);


CREATE INDEX IF NOT EXISTS idx_analysis_results_server
ON analysis_results (server);


CREATE INDEX IF NOT EXISTS idx_analysis_results_severity
ON analysis_results (severity);


CREATE INDEX IF NOT EXISTS idx_analysis_results_source
ON analysis_results (source);


CREATE INDEX IF NOT EXISTS idx_analysis_results_rag_knowledge_id
ON analysis_results (rag_knowledge_id);


CREATE INDEX IF NOT EXISTS idx_analysis_results_jira_issue_key
ON analysis_results (jira_issue_key);


CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at
ON analysis_results (created_at DESC);