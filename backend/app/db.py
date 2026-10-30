import asyncio
from pathlib import Path
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb
from psycopg_pool import AsyncConnectionPool

from .config import Settings
from .eligibility import normalized
from .models import AgentResult, ExtractionSnapshot, ResearchRun, Scholarship
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
            await conn.execute((Path(__file__).parent / "migrations/003_extraction_history.sql").read_text())

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
                 Jsonb(scholarship.model_dump(mode="json", exclude={"id", "updated_at"}))),
            )

            # A snapshot and the latest record commit or roll back together. No profiles are stored.
            await conn.execute(
                "INSERT INTO scholarship_extractions(scholarship_id,data) "
                "SELECT id,data FROM scholarships WHERE source_url=%s AND normalized_name=%s",
                (str(scholarship.source_url), normalized(scholarship.name)),
            )

    async def save_research(self, result: AgentResult) -> str:
        if result.mode != "RESEARCH" or result.matches:
            raise ValueError("Only research without student matching may be retained")
        identifier = uuid4()
        snapshot = result.model_copy(update={"research_id": str(identifier)})
        async with self.require().connection() as conn, conn.transaction():
            await conn.execute("INSERT INTO research_runs(id,query,result) VALUES (%s,%s,%s)",
                               (identifier, result.query, Jsonb(snapshot.model_dump(mode="json"))))
        return str(identifier)

    async def research_history(self, limit: int = 10) -> list[ResearchRun]:
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT id,query,created_at,jsonb_array_length(result->'scholarships') FROM research_runs "
                "ORDER BY created_at DESC,id DESC LIMIT %s", (limit,),
            )
            return [ResearchRun(id=str(row[0]), query=row[1], created_at=row[2], scholarship_count=row[3])
                    for row in await cursor.fetchall()]

    async def research_detail(self, identifier: UUID) -> AgentResult | None:
        async with self.require().connection() as conn:
            cursor = await conn.execute("SELECT result FROM research_runs WHERE id=%s", (identifier,))
            row = await cursor.fetchone()
            return AgentResult.model_validate(row[0]) if row else None

    async def by_id(self, scholarship_id: int) -> Scholarship | None:
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT data || jsonb_build_object('id',id,'updated_at',updated_at) "
                "FROM scholarships WHERE id=%s", (scholarship_id,),
            )
            row = await cursor.fetchone()
            return Scholarship.model_validate(row[0]) if row else None

    async def extraction_history(self, scholarship_id: int, limit: int = 20) -> list[ExtractionSnapshot]:
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT id,recorded_at,data FROM scholarship_extractions WHERE scholarship_id=%s "
                "ORDER BY recorded_at DESC,id DESC LIMIT %s", (scholarship_id, limit),
            )
            return [ExtractionSnapshot(id=row[0], recorded_at=row[1], scholarship=Scholarship.model_validate(row[2]))
                    for row in await cursor.fetchall()]

    async def get(self, source_url: str, name: str) -> Scholarship | None:
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT data || jsonb_build_object('id',id,'updated_at',updated_at) "
                "FROM scholarships WHERE source_url=%s AND normalized_name=%s",
                (source_url, normalized(name)),
            )
            row = await cursor.fetchone()
            return Scholarship.model_validate(row[0]) if row else None

    async def list(self, limit: int = 30):
        async with self.require().connection() as conn:
            cursor = await conn.execute(
                "SELECT data || jsonb_build_object('id',id,'updated_at',updated_at) "
                "FROM scholarships ORDER BY updated_at DESC,id DESC LIMIT %s", (limit,)
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
