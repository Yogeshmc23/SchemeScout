-- Optional capability only. Requires pgvector installed on the PostgreSQL server.
-- Does NOT establish embedding generation, storage or semantic retrieval.
CREATE EXTENSION IF NOT EXISTS vector;
INSERT INTO schema_migrations(version) VALUES (2) ON CONFLICT DO NOTHING;
