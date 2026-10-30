from unittest.mock import AsyncMock

import pytest

from app.models import AgentRequest, Page, Source
from app.security import ServiceError
from app.workflow import Workflow


@pytest.mark.parametrize("mode", ["DISCOVER", "RESEARCH"])
async def test_real_graph_routes_with_test_doubles(profile, scholarship, mode):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = [Source(title="Test source", url=scholarship.source_url, official=True)]
    tinyfish.fetch.return_value = ([Page(url=scholarship.source_url, content="All students may apply.")], [])
    ollama.extract.return_value = scholarship
    db.get.return_value = scholarship
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode=mode, query="fixture query", profile=profile))
    assert result.stored_count == 1
    db.save.assert_awaited_once_with(scholarship)
    assert len(result.matches) == (1 if mode == "DISCOVER" else 0)
    if mode == "DISCOVER":
        assert result.matches[0].status == "ELIGIBLE"


async def test_failed_fetch_never_extracts(profile):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = [Source(title="Test source", url="https://scholarships.gov.in/a", official=True)]
    tinyfish.fetch.side_effect = ServiceError("source unavailable", 502)
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="DISCOVER", query="fixture query", profile=profile))
    assert result.stored_count == 0 and result.errors
    ollama.extract.assert_not_awaited()
    db.save.assert_not_awaited()


async def test_third_party_never_confirms(profile):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = [Source(title="Test third party", url="https://example.org/a", official=False)]
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="RESEARCH", query="fixture query"))
    tinyfish.fetch.assert_not_awaited()
    assert result.errors and not result.scholarships


async def test_storage_failure_not_silently_successful(profile, scholarship):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = [Source(title="Test source", url=scholarship.source_url, official=True)]
    tinyfish.fetch.return_value = ([Page(url=scholarship.source_url, content="All students may apply.")], [])
    ollama.extract.return_value = scholarship
    db.get.return_value = scholarship
    db.save.side_effect = ServiceError("database unavailable")
    with pytest.raises(ServiceError):
        await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="DISCOVER", query="fixture query", profile=profile))


async def test_directory_detail_hop_is_bounded_and_persisted(profile, scholarship):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    portal = "https://scholarships.gov.in/"
    links = [f"https://scholarships.gov.in/scheme/{i}" for i in range(10)]
    tinyfish.search.return_value = [Source(title="Portal", url=portal, official=True)]
    async def fetch(urls):
        return ([Page(url=u, content="test page", links=links if u == portal else []) for u in urls], [])
    tinyfish.fetch.side_effect = fetch
    ollama.extract.side_effect = [ServiceError("Directory, not a scholarship"), scholarship, scholarship, scholarship]
    db.get.return_value = scholarship
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="DISCOVER", query="fixture query", profile=profile))
    assert tinyfish.fetch.await_count == 4  # one initial page + three detail pages, no recursion
    assert result.query == "fixture query"
    assert result.stored_count == 1
    db.get.assert_awaited_once_with(str(scholarship.source_url), scholarship.name)
    assert sum(o.stage == "DETAIL_FETCH" and o.status == "SUCCESS" for o in result.source_outcomes) == 3


async def test_missing_read_after_write_fails(profile, scholarship):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = [Source(title="Test", url=scholarship.source_url, official=True)]
    tinyfish.fetch.return_value = ([Page(url=scholarship.source_url, content="test")], [])
    ollama.extract.return_value = scholarship
    db.get.return_value = None
    with pytest.raises(ServiceError, match="could not be retrieved"):
        await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="DISCOVER", query="fixture query", profile=profile))


async def test_chat_returns_grounding_sources(scholarship):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    db.list.return_value = [scholarship]
    ollama.answer.return_value = "Evidence-backed test answer"
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="CHAT", query="What documents are required?"))
    assert result.sources[0].url == scholarship.source_url
    assert result.query == "What documents are required?"


async def test_chat_does_not_attach_irrelevant_records(scholarship):
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    db.list.return_value = [scholarship]
    ollama.answer.return_value = "No relevant evidence"
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode="CHAT", query="Unrelated opportunity query"))
    assert not result.sources
    ollama.answer.assert_awaited_once_with("Unrelated opportunity query", [])


async def test_graph_execution_has_explicit_safe_stages():
    db, tinyfish, ollama = AsyncMock(), AsyncMock(), AsyncMock()
    tinyfish.search.return_value = []
    result = await Workflow(db, tinyfish, ollama).run(AgentRequest(mode='RESEARCH', query='fixture query'))
    stages = [entry.stage for entry in result.execution]
    assert stages == ['validate_input', 'classify', 'search', 'fetch', 'extract', 'validate_records', 'store', 'retrieve', 'summarize']
    assert all(entry.duration_ms >= 0 and entry.status == 'SUCCESS' for entry in result.execution)
    assert len(result.workflow_id) == 32
