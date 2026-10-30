"""TinyFish MCP Search/Fetch transport, mapping and source-safe acquisition."""
import asyncio
import json
import re
from contextlib import AsyncExitStack
from datetime import UTC, datetime
from urllib.parse import urljoin

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import ValidationError

from ..config import Settings
from ..models import Page, Source
from ..security import ServiceError, is_official, public_official_url, safe_url


def result_items(raw, operation: str) -> list:
    """Fail closed on undocumented envelope shapes, including null or strings."""
    items = raw if isinstance(raw, list) else raw.get("results") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        raise ServiceError(f"TinyFish {operation} returned an unsupported results envelope.", 502)
    return items


class TinyFish:
    """Official hosted MCP Search/Fetch API, not metered browser automation."""

    def __init__(self, config: Settings):
        self.config = config

    async def call(self, name: str, arguments: dict):
        if not self.config.tinyfish_api_key:
            raise ServiceError("TinyFish is not configured. Set TINYFISH_API_KEY on the backend.")
        try:
            async with asyncio.timeout(self.config.request_timeout):
                async with AsyncExitStack() as stack:
                    transport = await stack.enter_async_context(streamablehttp_client(
                        "https://agent.tinyfish.ai/mcp",
                        headers={"X-API-Key": self.config.tinyfish_api_key.get_secret_value()},
                    ))
                    session = await stack.enter_async_context(ClientSession(transport[0], transport[1]))
                    await session.initialize()
                    result = await asyncio.wait_for(session.call_tool(name, arguments), timeout=self.config.request_timeout)
                    if result.isError:
                        raise ServiceError(f"TinyFish {name} reported a failure. Check provider access and usage limits.", 502)
                    if result.structuredContent is not None:
                        return result.structuredContent
                    texts = [block.text for block in result.content if block.type == "text"]
                    if not texts:
                        raise ValueError("No text result")
                    return json.loads("\n".join(texts))
        except TimeoutError:
            raise ServiceError(f"TinyFish {name} exceeded its time budget.", 504) from None
        except ServiceError:
            raise
        except Exception:  # noqa: BLE001 -- provider SDK may wrap failures in ExceptionGroup
            raise ServiceError(f"TinyFish {name} is unavailable or returned an unsupported response.", 502) from None

    async def search(self, query: str) -> list[Source]:
        raw = await self.call("search", {
            "query": query, "purpose": "Find official Indian student scholarship eligibility and applications",
            "location": "IN", "language": "en", "domain_type": "web",
        })
        items = result_items(raw, "search")
        sources = []
        for item in items[:20]:
            try:
                url = safe_url(item["url"])
                sources.append(Source(
                    title=str(item.get("title") or url)[:1000], url=url,
                    snippet=str(item.get("snippet") or item.get("description") or "")[:6000],
                    official=is_official(url),
                ))
            except (KeyError, TypeError, ValidationError, ServiceError):
                continue
        return sorted(sources, key=lambda s: not s.official)[:8]

    async def fetch(self, urls: list[str]) -> tuple[list[Page], list[str]]:
        if not 1 <= len(urls) <= 3:
            raise ServiceError("Fetch accepts between one and three URLs.", 422)
        urls = [await public_official_url(url) for url in urls]
        raw = await self.call("fetch_content", {
            "urls": urls, "format": "markdown", "links": True, "image_links": False,
            "page_metadata": False, "ttl": 0, "per_url_timeout_ms": 25000,
        })
        items = result_items(raw, "fetch")
        pages, errors, received = [], [], set()
        for item in items:
            try:
                url = safe_url(item["url"], official_only=True)
                status = item.get("status_code", 200)
                if isinstance(status, bool) or not isinstance(status, int):
                    raise TypeError()
                if url not in urls or item.get("error") or not 200 <= status < 300:
                    raise ValueError()
                # Refuse a provider-reported redirect outside the maintained policy.
                if item.get("final_url"):
                    await public_official_url(item["final_url"])
                    if safe_url(item["final_url"]) != url:
                        raise ValueError()
                text = item.get("text") or item.get("markdown") or item.get("content")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError()
                links = []
                reported = item.get("links", [])
                if not isinstance(reported, list):
                    reported = []
                # Only actual returned links or markdown hrefs, never model-invented URLs.
                candidates = reported[:100] + re.findall(r"\[[^\]]+\]\(([^\s)]+)\)", text)[:100]
                for candidate in candidates:
                    href = candidate.get("url") or candidate.get("href") if isinstance(candidate, dict) else candidate
                    if not isinstance(href, str):
                        continue
                    try:
                        link = safe_url(urljoin(url, href), official_only=True)
                        if link != url and link not in links:
                            links.append(link)
                    except ServiceError:
                        continue
                pages.append(Page(url=url, content=text[:40000], links=links[:30], truncated=len(text) > 40000, fetched_at=datetime.now(UTC)))
                received.add(url)
            except (KeyError, TypeError, ValueError, ServiceError):
                continue
        for url in urls:
            if url not in received:
                errors.append(f"No successful, policy-approved page content returned for {url}")
        return pages, errors

