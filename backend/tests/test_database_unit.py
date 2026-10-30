"""SQL/lifecycle unit tests with explicit DB doubles; not PostgreSQL connectivity proof."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import Settings
from app.db import Database
from app.security import ServiceError


@pytest.fixture
def database_double():
    db = Database(Settings(database_url=None))
    conn = AsyncMock()
    conn.transaction = MagicMock()
    conn.transaction.return_value.__aenter__ = AsyncMock()
    conn.transaction.return_value.__aexit__ = AsyncMock(return_value=False)
    pool = MagicMock()
    pool.connection.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.connection.return_value.__aexit__ = AsyncMock(return_value=False)
    db.pool = pool
    return db, conn


async def test_incompatible_legacy_table_is_not_modified(database_double):
    db, conn = database_double
    cursor = AsyncMock()
    cursor.fetchall.return_value = [("id",), ("name",), ("states",)]
    conn.execute.side_effect = [None, cursor]
    with pytest.raises(ServiceError, match="incompatible"):
        await db.migrate()
    assert conn.execute.await_count == 2  # lock and inspection only; no CREATE/ALTER/DROP


async def test_new_schema_applied_under_transaction(database_double):
    db, conn = database_double
    cursor = AsyncMock()
    cursor.fetchall.return_value = []
    conn.execute.side_effect = [None, cursor, None]
    await db.migrate()
    assert "pg_advisory_xact_lock" in conn.execute.call_args_list[0].args[0]
    assert "CREATE TABLE IF NOT EXISTS scholarships" in conn.execute.call_args_list[-1].args[0]
    conn.transaction.return_value.__aexit__.assert_awaited_once()


async def test_save_uses_parameters_and_one_transaction(database_double, scholarship):
    db, conn = database_double
    scholarship.name = "Robert'); DROP TABLE scholarships; --"
    await db.save(scholarship)
    assert conn.execute.await_count == 2
    sql, parameters = conn.execute.call_args.args
    assert scholarship.name not in sql
    assert parameters[2] == scholarship.name
    conn.transaction.assert_called_once()


async def test_identity_read_reconstructs_validated_record(database_double, scholarship):
    db, conn = database_double
    cursor = AsyncMock()
    cursor.fetchone.return_value = (scholarship.model_dump(mode="json"),)
    conn.execute.return_value = cursor
    record = await db.get(str(scholarship.source_url), " SYNTHETIC test scholarship ")
    assert record == scholarship
    assert conn.execute.call_args.args[1] == (str(scholarship.source_url), "synthetic test scholarship")


async def test_missing_identity_returns_none(database_double):
    db, conn = database_double
    cursor = AsyncMock()
    cursor.fetchone.return_value = None
    conn.execute.return_value = cursor
    assert await db.get("https://scholarships.gov.in/missing", "Missing") is None
