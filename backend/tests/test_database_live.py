import os
from datetime import UTC, datetime

import pytest

from app.config import Settings
from app.db import Database


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires a dedicated TEST_DATABASE_URL PostgreSQL database")
async def test_postgres_migration_upsert_and_retrieval(scholarship):
    # Use a dedicated test database: migration persists and a synthetic fixture is inserted then removed.
    db = Database(Settings(database_url=os.environ["TEST_DATABASE_URL"]))
    scholarship.fetched_at = datetime.now(UTC)
    await db.open()
    try:
        await db.migrate()
        await db.migrate()
        await db.health()
        await db.save(scholarship)
        await db.save(scholarship)
        reloaded = await db.get(str(scholarship.source_url), scholarship.name)
        assert reloaded.id is not None
        assert reloaded.model_dump(exclude={"id", "updated_at"}) == scholarship.model_dump(exclude={"id", "updated_at"})
        assert (await db.by_id(reloaded.id)).name == scholarship.name
        assert len(await db.extraction_history(reloaded.id)) == 2
        records = await db.list()
        assert any(s.name == scholarship.name for s in records)
        async with db.require().connection() as conn:
            cur = await conn.execute("SELECT count(*) FROM scholarships WHERE source_url=%s", (str(scholarship.source_url),))
            assert (await cur.fetchone())[0] == 1
    finally:
        if db.pool:
            async with db.pool.connection() as conn:
                await conn.execute("DELETE FROM scholarship_extractions WHERE scholarship_id IN "
                                   "(SELECT id FROM scholarships WHERE source_url=%s)", (str(scholarship.source_url),))
                await conn.execute("DELETE FROM scholarships WHERE source_url=%s", (str(scholarship.source_url),))
                await conn.execute("DELETE FROM scholarship_sources WHERE url=%s", (str(scholarship.source_url),))
        await db.close()
