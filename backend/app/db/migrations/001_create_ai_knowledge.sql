-- ============================================================================
-- AI LOG ANALYZER
-- Migration: 001_create_ai_knowledge
--
-- Purpose:
--     Create the RAG knowledge store for previously analyzed/resolved errors.
--
-- Important:
--     This table is intentionally generic so it can store knowledge from:
--       - Web
--       - Telephony
--       - MySQL
--       - Future log types
--
-- Embedding model for initial implementation:
--     OpenAI text-embedding-3-small
--     Dimension: 1536
-- ============================================================================


-- ----------------------------------------------------------------------------
-- Enable pgvector
-- ----------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS vector;


-- ----------------------------------------------------------------------------
-- Main RAG knowledge table
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ai_knowledge_items (

    id BIGSERIAL PRIMARY KEY,


    -- ========================================================================
    -- SOURCE INFORMATION
    -- ========================================================================

    tier VARCHAR(50) NOT NULL,

    log_type VARCHAR(100) NOT NULL,

    server VARCHAR(255),

    file_name VARCHAR(500),

    file_path TEXT,


    -- ========================================================================
    -- ERROR IDENTIFICATION
    -- ========================================================================

    error_id VARCHAR(100),

    error_signature VARCHAR(500),

    title TEXT,

    severity VARCHAR(50),

    timestamp TEXT,


    -- ========================================================================
    -- ORIGINAL ERROR DATA
    -- ========================================================================

    error_content TEXT,

    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,


    -- ========================================================================
    -- AI ANALYSIS
    -- ========================================================================

    root_cause TEXT,

    root_cause_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,

    solution TEXT,

    optimization TEXT,

    test_result JSONB NOT NULL DEFAULT '{}'::jsonb,

    jira_description TEXT,


    -- ========================================================================
    -- RESOLUTION INFORMATION
    -- ========================================================================

    resolution_status VARCHAR(50) NOT NULL DEFAULT 'unknown',

    verified BOOLEAN NOT NULL DEFAULT FALSE,

    verification_notes TEXT,


    -- ========================================================================
    -- RAG INFORMATION
    -- ========================================================================

    /*
     * Text representation used to create the embedding.
     *
     * We deliberately store this text so that we can inspect exactly what
     * information was embedded into the vector.
     */
    embedding_text TEXT,

    /*
     * Initial embedding dimension:
     *
     * OpenAI text-embedding-3-small = 1536 dimensions
     */
    embedding VECTOR(1536),


    -- ========================================================================
    -- EXTENSIBLE METADATA
    -- ========================================================================

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,


    -- ========================================================================
    -- AUDIT
    -- ========================================================================

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);


-- ============================================================================
-- INDEXES
-- ============================================================================


-- ----------------------------------------------------------------------------
-- Exact error lookup
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_error_signature
ON ai_knowledge_items (error_signature);


-- ----------------------------------------------------------------------------
-- Log type filtering
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_log_type
ON ai_knowledge_items (log_type);


-- ----------------------------------------------------------------------------
-- Tier filtering
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_tier
ON ai_knowledge_items (tier);


-- ----------------------------------------------------------------------------
-- Resolution filtering
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_resolution_status
ON ai_knowledge_items (resolution_status);


-- ----------------------------------------------------------------------------
-- Verified resolution filtering
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_verified
ON ai_knowledge_items (verified);


-- ----------------------------------------------------------------------------
-- Metadata search
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_metadata
ON ai_knowledge_items
USING GIN (metadata);


-- ============================================================================
-- VECTOR INDEX
-- ============================================================================

/*
 * HNSW gives us efficient approximate nearest-neighbor searches.
 *
 * cosine distance is appropriate for semantic similarity.
 */

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_embedding
ON ai_knowledge_items
USING hnsw (embedding vector_cosine_ops);