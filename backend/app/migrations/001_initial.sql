CREATE TABLE IF NOT EXISTS schema_migrations (
    version integer PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS scholarship_sources (
    url text PRIMARY KEY,
    evidence text NOT NULL,
    fetched_at timestamptz NOT NULL,
    official boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS scholarships (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_url text NOT NULL REFERENCES scholarship_sources(url),
    normalized_name text NOT NULL,
    name text NOT NULL,
    data jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_url, normalized_name)
);
CREATE INDEX IF NOT EXISTS scholarships_updated_idx ON scholarships(updated_at DESC);
CREATE INDEX IF NOT EXISTS scholarships_rules_idx ON scholarships USING gin ((data->'rules'));
INSERT INTO schema_migrations(version) VALUES (1) ON CONFLICT DO NOTHING;
