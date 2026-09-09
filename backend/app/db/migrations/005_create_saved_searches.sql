-- =============================================================================
-- PHASE 4 - SAVED SEARCHES
-- =============================================================================
--
-- A saved search is created ONLY when the user explicitly clicks
-- "Save Search".
--
-- Normal searches must NOT create records in this table.
--
-- Automation does NOT use this table.
-- =============================================================================

CREATE TABLE IF NOT EXISTS saved_searches (

    id BIGSERIAL PRIMARY KEY,

    user_id UUID NOT NULL,

    name VARCHAR(255) NOT NULL,

    description TEXT,

    from_date DATE NOT NULL,

    to_date DATE NOT NULL,

    tier VARCHAR(30) NOT NULL,

    servers JSONB NOT NULL DEFAULT '[]'::jsonb,

    search_filters JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_saved_searches_user
        FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_saved_searches_date_range
        CHECK (to_date >= from_date)

);


-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id
ON saved_searches (user_id);

CREATE INDEX IF NOT EXISTS idx_saved_searches_user_created
ON saved_searches (
    user_id,
    created_at DESC
);

CREATE INDEX IF NOT EXISTS idx_saved_searches_tier
ON saved_searches (tier);