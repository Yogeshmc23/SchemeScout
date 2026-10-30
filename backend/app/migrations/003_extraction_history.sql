-- Additive: existing source/scholarship rows and identities are preserved.
CREATE TABLE IF NOT EXISTS scholarship_extractions (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scholarship_id bigint NOT NULL REFERENCES scholarships(id),
    data jsonb NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS scholarship_extractions_record_idx
    ON scholarship_extractions(scholarship_id, recorded_at DESC);
-- Opt-in research history contains queries and public evidence, never student profiles/matches.
CREATE TABLE IF NOT EXISTS research_runs (
    id uuid PRIMARY KEY,
    query text NOT NULL,
    result jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (result->>'mode' = 'RESEARCH'),
    CHECK (result->'matches' = '[]'::jsonb)
);
CREATE INDEX IF NOT EXISTS research_runs_created_idx ON research_runs(created_at DESC);
INSERT INTO schema_migrations(version) VALUES (3) ON CONFLICT DO NOTHING;
