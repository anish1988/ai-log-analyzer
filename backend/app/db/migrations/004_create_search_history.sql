-- =============================================================================
-- PHASE 4 - SEARCH HISTORY
-- =============================================================================
--
-- Purpose:
--   Persist searches performed by application users.
--
-- Important:
--   This table is ONLY for manual/user initiated searches.
--
--   Automation runs MUST NOT write to this table.
--
-- =============================================================================

CREATE TABLE IF NOT EXISTS search_history (

    id BIGSERIAL PRIMARY KEY,

    user_id UUID NOT NULL,

    search_id UUID NOT NULL DEFAULT gen_random_uuid(),

    from_date DATE NOT NULL,

    to_date DATE NOT NULL,

    tier VARCHAR(30) NOT NULL,

    servers JSONB NOT NULL DEFAULT '[]'::jsonb,

    search_filters JSONB NOT NULL DEFAULT '{}'::jsonb,

    total_results INTEGER NOT NULL DEFAULT 0,

    status VARCHAR(30) NOT NULL DEFAULT 'completed',

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_search_history_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT uq_search_history_search_id
        UNIQUE (search_id),

    CONSTRAINT chk_search_history_status
        CHECK (
            status IN (
                'started',
                'completed',
                'failed'
            )
        )

);


-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_search_history_user_id
ON search_history (user_id);

CREATE INDEX IF NOT EXISTS idx_search_history_created_at
ON search_history (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_search_history_user_created
ON search_history (
    user_id,
    created_at DESC
);

CREATE INDEX IF NOT EXISTS idx_search_history_status
ON search_history (status);

CREATE INDEX IF NOT EXISTS idx_search_history_tier
ON search_history (tier);