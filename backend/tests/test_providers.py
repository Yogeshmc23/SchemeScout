from unittest.mock import AsyncMock

import httpx
import pytest
from pydantic import HttpUrl

from app.config import Settings
from app.models import Page
from app.providers import Ollama, TinyFish
from app.security import ServiceError


async def test_tinyfish_missing_configuration():
    with pytest.raises(ServiceError, match="not configured"):
        await TinyFish(Settings(tinyfish_api_key=None)).search("scholarships")


async def test_search_contract_fixture(monkeypatch):
    provider = TinyFish(Settings())
    monkeypatch.setattr(provider, "call", AsyncMock(return_value={"results": [
        {"title": "Third party", "url": "https://example.org/a", "snippet": "unconfirmed"},
        {"title": "Official", "url": "https://scholarships.gov.in/a", "snippet": "official"},
        {"title": "Unsafe", "url": "file:///etc/passwd"},
    ]}))
    sources = await provider.search("test scholarships")
    assert len(sources) == 2
    assert sources[0].official and not sources[1].official
    provider.call.assert_awaited_once()


async def test_fetch_partial_failure(monkeypatch):
    provider = TinyFish(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "call", AsyncMock(return_value={"results": [
        {"url": "https://scholarships.gov.in/a", "text": "Content"},
        {"url": "https://scholarships.gov.in/b", "error": "unreachable"},
    ]}))
    pages, errors = await provider.fetch(["https://scholarships.gov.in/a", "https://scholarships.gov.in/b"])
    assert len(pages) == 1 and len(errors) == 1
    assert "/b" in errors[0]
    assert provider.call.call_args.args[0] == "fetch_content"


async def test_fetch_redirect_rejected(monkeypatch):
    provider = TinyFish(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "call", AsyncMock(return_value={"results": [
        {"url": "https://scholarships.gov.in/a", "final_url": "https://evil.com/", "text": "fake"},
    ]}))
    pages, errors = await provider.fetch(["https://scholarships.gov.in/a"])
    assert not pages and errors


async def test_fetch_limits():
    with pytest.raises(ServiceError):
        await TinyFish(Settings()).fetch([])


async def test_ollama_http_failure(monkeypatch):
    monkeypatch.setattr(httpx.AsyncClient, "post", AsyncMock(side_effect=httpx.ConnectError("offline")))
    with pytest.raises(ServiceError, match="Ollama"):
        await Ollama(Settings()).generate("system", "prompt")


async def test_extraction_validates_and_overrides_provenance(monkeypatch, scholarship):
    provider = Ollama(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    scholarship.source_url = HttpUrl("https://example.org/forged")
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    page = Page(url="https://scholarships.gov.in/a", content="Synthetic test scholarship. All students may apply.")
    data = await provider.extract(page)
    assert str(data.source_url) == str(page.url)
    assert data.official_source and data.fetched_at
    assert data.source_evidence == page.content


@pytest.mark.parametrize("text", ["not json", "{}", '{"name":"X","unknown":1}'])
async def test_malformed_extraction(monkeypatch, text):
    provider = Ollama(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=text))
    with pytest.raises(ServiceError, match="validation"):
        await provider.extract(Page(url="https://scholarships.gov.in/a", content="test content"))


async def test_fabricated_rule_evidence_rejected(monkeypatch, scholarship):
    provider = Ollama(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    with pytest.raises(ServiceError):
        await provider.extract(Page(url="https://scholarships.gov.in/a", content="Entirely different source"))


async def test_chat_without_evidence_does_not_invent():
    answer = await Ollama(Settings()).answer("How much funding?", [])
    assert "cannot verify" in answer


async def test_invented_benefit_rejected(monkeypatch, scholarship):
    provider = Ollama(Settings())
    scholarship.benefits = "Invented award of INR 100000"
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    with pytest.raises(ServiceError):
        await provider.extract(Page(url="https://scholarships.gov.in/a",
                                    content="Synthetic test scholarship. All students may apply."))


async def test_ungrounded_deadline_removed(monkeypatch, scholarship):
    from datetime import date
    provider = Ollama(Settings())
    scholarship.deadline = date(2030, 1, 1)
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    data = await provider.extract(Page(url="https://scholarships.gov.in/a",
                                       content="Synthetic test scholarship. All students may apply."))
    assert data.deadline is None
    assert any("Deadline" in s for s in data.missing_information)


@pytest.mark.parametrize("raw", [None, "invalid", 17, True, {}, {"results": {}}, {"results": None}])
async def test_invalid_search_envelopes_return_service_error(monkeypatch, raw):
    provider = TinyFish(Settings())
    monkeypatch.setattr(provider, "call", AsyncMock(return_value=raw))
    with pytest.raises(ServiceError) as error:
        await provider.search("scholarship query")
    assert error.value.code == 502


@pytest.mark.parametrize("raw", [None, "invalid", [], {"message": None}, {"message": {"content": 42}}])
async def test_invalid_ollama_envelopes(monkeypatch, raw):
    response = httpx.Response(200, json=raw, request=httpx.Request("POST", "http://ollama/api/chat"))
    monkeypatch.setattr(httpx.AsyncClient, "post", AsyncMock(return_value=response))
    with pytest.raises(ServiceError) as error:
        await Ollama(Settings()).generate("system", "prompt")
    assert error.value.code == 502


async def test_fetch_preserves_safe_links_and_acquisition_time(monkeypatch):
    provider = TinyFish(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "call", AsyncMock(return_value={"results": [{
        "url": "https://scholarships.gov.in/", "text": "[Scheme](/scheme/one)",
        "links": [{"href": "/scheme/two"}, {"url": "https://evil.com/scheme"}, "javascript:alert(1)"],
    }]}))
    pages, errors = await provider.fetch(["https://scholarships.gov.in/"])
    assert not errors and pages[0].fetched_at
    assert {str(u) for u in pages[0].links} == {"https://scholarships.gov.in/scheme/one", "https://scholarships.gov.in/scheme/two"}
    assert provider.call.call_args.args[1]["links"] is True


async def test_fabricated_numeric_bound_rejected(monkeypatch, scholarship):
    from app.models import Criterion
    provider = Ollama(Settings())
    scholarship.rules.annual_income = Criterion(status="RESTRICTED", maximum=500000,
                                               evidence="Annual income must not exceed 250000.")
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    with pytest.raises(ServiceError):
        await provider.extract(Page(url="https://scholarships.gov.in/a",
                                    content="Synthetic test scholarship. All students may apply. Annual income must not exceed 250000."))


async def test_currency_units_are_grounded(monkeypatch, scholarship):
    from app.models import Criterion
    provider = Ollama(Settings())
    scholarship.rules.annual_income = Criterion(status="RESTRICTED", maximum=250000,
                                               maximum_exclusive=True, evidence="Annual income below INR 2.5 lakh.")
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    page = Page(url="https://scholarships.gov.in/a",
                content="Synthetic test scholarship. All students may apply. Annual income below INR 2.5 lakh.")
    data = await provider.extract(page)
    assert data.rules.annual_income.maximum == 250000
    assert data.fetched_at == page.fetched_at


async def test_mcp_initialization_timeout_is_bounded(monkeypatch):
    import asyncio
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def stuck_transport(*args, **kwargs):
        await asyncio.sleep(1)
        yield (None, None, None)

    monkeypatch.setattr("app.providers.streamablehttp_client", stuck_transport)
    config = Settings(tinyfish_api_key="synthetic-test-key")
    config.request_timeout = 0.01
    with pytest.raises(ServiceError):
        await TinyFish(config).call("search", {"query": "test"})


async def test_truncated_pages_cannot_claim_full_eligibility(monkeypatch, scholarship):
    provider = Ollama(Settings())
    monkeypatch.setattr("app.providers.public_official_url", AsyncMock(side_effect=lambda u: u))
    monkeypatch.setattr(provider, "generate", AsyncMock(return_value=scholarship.model_dump_json()))
    page = Page(url="https://scholarships.gov.in/a", truncated=True,
                content="Synthetic test scholarship. All students may apply.")
    data = await provider.extract(page)
    assert not data.eligibility_complete
    assert data.extraction_status == "PARTIAL"
    assert any("truncated" in value for value in data.missing_information)


async def test_ollama_timeout_has_explicit_status(monkeypatch):
    monkeypatch.setattr(httpx.AsyncClient, "post", AsyncMock(side_effect=httpx.ReadTimeout("private detail")))
    with pytest.raises(ServiceError) as error:
        await Ollama(Settings()).generate("system", "prompt")
    assert error.value.code == 504
    assert "private detail" not in error.value.message
