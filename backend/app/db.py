import asyncio
from pathlib import Path

from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from .config import Settings
from .eligibility import normalized
from .models import Scholarship
from .security import ServiceError


class Database:
    def __init__(self, config: Settings):
        self.pool = None
        if config.database_url:
            self.pool = AsyncConnectionPool(
                config.database_url.get_secret_value(), open=False, min_size=0, max_size=5,
                timeout=5, kwargs={"connect_timeout": 5},
            )

    def require(self):
        if self.pool is None:
            raise ServiceError("PostgreSQL is not configured. Set DATABASE_URL on the backend.")
        return self.pool

    async def open(self):
        if self.pool:
            await self.pool.open()

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def migrate(self):
        sql = (Path(__file__).parent / "migrations/001_initial.sql").read_text()
        async with self.require().connection() as conn, conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(741920)")
            columns = await conn.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = current_schema() AND table_name = 'scholarships'"
            )
            existing = {row[0] for row in await columns.fetchall()}
            required = {"id", "source_url", "normalized_name", "name", "data", "updated_at"}
            if existing and not required.issubset(existing):
                raise ServiceError(
                    "An incompatible scholarships table exists. Back up and review its migration before continuing."
                )
            await conn.execute(sql)

    async def health(self):
        async with self.require().connection() as conn:
            await conn.execute("SELECT 1 FROM scholarships LIMIT 1")

    async def save(self, scholarship: Scholarship):
        async with self.require().connection() as conn, conn.transaction():
            await conn.execute(
                "INSERT INTO scholarship_sources(url,evidence,fetched_at,official) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT(url) DO UPDATE SET evidence=excluded.evidence, fetched_at=excluded.fetched_at, "
                "official=excluded.official",
                (str(scholarship.source_url), scholarship.source_evidence,
                 scholarship.fetched_at, scholarship.official_source),
            )
            await conn.execute(
                "INSERT INTO scholarships(source_url,normalized_name,name,data) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT(source_url,normalized_name) DO UPDATE SET name=excluded.name, "
                "data=excluded.data,updated_at=now()",
                (str(scholarship.source_url), normalized(scholarship.name), scholarship.name,
                 Jsonb(scholarship.model_dump(mode="json"))),
            )

    async def get(self, source_url: str, name: str) -> Scholarship | None:
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT data FROM scholarships WHERE source_url=%s AND normalized_name=%s",
                (source_url, normalized(name)),
            )
            row = await cursor.fetchone()
            return Scholarship.model_validate(row[0]) if row else None

    async def list(self, limit: int = 30):
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT data FROM scholarships ORDER BY updated_at DESC LIMIT %s", (limit,)
            )
            return [Scholarship.model_validate(row[0]) for row in await cursor.fetchall()]


async def migrate():
    from .config import settings
    db = Database(settings())
    await db.open()
    try:
        await db.migrate()
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(migrate())
